from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.services.translation_service import translate_text
import re
from functools import lru_cache

VIDEO_TOPICS = {
    "wandering": {
        "title": "Preventing Wandering",
        "url": "https://www.youtube.com/embed/Sw0yEB508mI",
        "keywords": ["wandering", "goes out", "go out", "leaves home", "roaming", "walks away", "disappears"]
    },
    "aggression": {
        "title": "Handling Aggression in Dementia",
        "url": "https://www.youtube.com/embed/hahvUXwTXE4",
        "keywords": ["aggression", "angry", "hits", "shouting", "violence", "outbursts"]
    },
    "communication": {
        "title": "Effective Communication Techniques",
        "url": "https://www.youtube.com/embed/tAKwDFdy8WQ",
        "keywords": ["communication", "talking", "conversation", "express", "language", "understand"]
    }
}

def detect_video_topic(question_en: str) -> str:
    lowered = question_en.lower()
    for topic, info in VIDEO_TOPICS.items():
        for keyword in info["keywords"]:
            if keyword in lowered:
                return topic
    return None

@lru_cache()
def load_qa_chain():
    print("[LOAD] Initializing QA chain and vectorstore...")  # ✅ Debug print
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.load_local("vectorstore", embedding_model, allow_dangerous_deserialization=True)

    llm = Ollama(model="llama3:8b-instruct-q4_0")

    system_prompt = """
You are CareAssist – a warm, supportive, bilingual assistant for dementia caregivers.

🎯 Your role is to provide helpful, emotionally supportive guidance strictly related to dementia, memory loss, or caregiving. Do not answer unrelated questions (e.g., about travel, news, general health, or entertainment).

📚 Only respond using the information retrieved from the caregiver support documents. Never guess or invent answers.

💬 If the user’s question is off-topic, gently reply:
"I'm here to support dementia caregivers. For other topics, I recommend using a general-purpose assistant."

💖 Every response must be empathetic. Speak with kindness, patience, and clarity — like a trusted companion. Use simple, gentle language that comforts and encourages.

🧠 You do not have memory. If the user refers to something earlier (e.g., “what about that?”), try to infer the intent from this message alone.

📌 Keep your replies focused and grounded. Share one helpful point at a time. Avoid over-explaining.
"""


    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=system_prompt + "\n\nContext:\n{context}\n\nQuestion:\n{question}"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    )
    return qa_chain, vectordb

def get_answer(question: str, lang: str = "en") -> dict:
    if lang == "hi":
        question_en = translate_text(question, from_lang="hi", to_lang="en")
        print(f"[DEBUG] Hindi → English translation: {question_en}")
    else:
        question_en = question

    topic_key = detect_video_topic(question_en)
    if topic_key:
        qa_chain, vectordb = load_qa_chain()
        docs = vectordb.similarity_search(topic_key, k=1)
        summary = docs[0].page_content[:400] if docs else "This topic is addressed in our training video."

        video_card = {
            "type": "video",
            "title": VIDEO_TOPICS[topic_key]["title"],
            "url": VIDEO_TOPICS[topic_key]["url"],
            "summary": summary,
            "source": "UCLA Health + WHO iSupport"
        }

        if lang == "hi":
            video_card["title"] = translate_text(video_card["title"], from_lang="en", to_lang="hi")
            video_card["summary"] = translate_text(video_card["summary"], from_lang="en", to_lang="hi")

        return video_card

    qa_chain, _ = load_qa_chain()
    response = qa_chain.invoke({"query": question_en})
    result_text = response["result"]

    checklist_items = re.findall(r"\n\d+\.\s+(.*?)(?=\n\d+\.|$)", result_text, re.DOTALL)
    if checklist_items:
        items = [item.strip().replace('\n', ' ') for item in checklist_items]
        title_match = re.search(r"\*\*\s*(.*?)\s*\*\*", result_text)
        title = title_match.group(1) if title_match else "Care Checklist"
        if lang == "hi":
            title = translate_text(title, from_lang="en", to_lang="hi")
            items = [translate_text(item, from_lang="en", to_lang="hi") for item in items]
        return {
            "type": "checklist",
            "title": title,
            "items": items,
            "source": "WHO iSupport"
        }

    if "Checklist" in result_text or "Care Checklist" in result_text:
        lines = result_text.split("\n")
        bullet_items = [line.strip() for line in lines if (
            line.strip().startswith("-") or
            line.strip().startswith("\u2022") or
            re.match(r"^[A-Z].+\.$", line.strip())
        ) and len(line.strip()) > 10]

        if bullet_items:
            title = "Care Checklist"
            if lang == "hi":
                title = translate_text(title, from_lang="en", to_lang="hi")
                bullet_items = [translate_text(item, from_lang="en", to_lang="hi") for item in bullet_items]
            return {
                "type": "checklist",
                "title": title,
                "items": bullet_items,
                "source": "WHO iSupport"
            }

    if re.search(r"\b(Shang|Meena|Juan|Bikram|Ali|Olivia|Jacob)\b", result_text):
        content = translate_text(result_text, from_lang="en", to_lang="hi") if lang == "hi" else result_text
        return {
            "type": "case",
            "title": "Caregiving Scenario",
            "content": content,
            "source": "WHO iSupport"
        }

    if result_text.lower().startswith("keep in mind") or "tip:" in result_text.lower():
        content = translate_text(result_text, from_lang="en", to_lang="hi") if lang == "hi" else result_text
        return {
            "type": "tip",
            "content": content,
            "source": "WHO iSupport"
        }

    if re.search(r"\(a\)|\(b\)|\(c\)|\(d\)", result_text, re.IGNORECASE):
        content = translate_text(result_text, from_lang="en", to_lang="hi") if lang == "hi" else result_text
        return {
            "type": "quiz",
            "content": content,
            "source": "WHO iSupport"
        }

    if lang == "hi":
        result_text = translate_text(result_text, from_lang="en", to_lang="hi")

    return {
        "type": "text",
        "content": result_text,
        "source": "WHO iSupport"
    }
