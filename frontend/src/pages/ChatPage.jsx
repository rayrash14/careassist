import Chat from "../components/Chat";

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="bg-indigo-600 text-white p-4 text-xl font-semibold text-center">
        CareAssist
      </div>
      <Chat />
    </div>
  );
}
