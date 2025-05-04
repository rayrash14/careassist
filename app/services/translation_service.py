import argostranslate.package
import argostranslate.translate

# Ensure models are loaded
installed_languages = argostranslate.translate.get_installed_languages()

# Utility function to translate between Hindi and English
def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    try:
        from_lang_obj = next(lang for lang in installed_languages if lang.code == from_lang)
        to_lang_obj = next(lang for lang in installed_languages if lang.code == to_lang)

        translation = from_lang_obj.get_translation(to_lang_obj)
        if not translation:
            raise ValueError(f"No translation path from '{from_lang}' to '{to_lang}'")

        return translation.translate(text)

    except Exception as e:
        print(f"[Translation Error] {e}")
        return text

