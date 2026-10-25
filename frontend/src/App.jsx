import { useEffect, useState } from "react";
import { getConfig } from "./api.js";
import Chat from "./components/Chat.jsx";
import Docs from "./components/Docs.jsx";
import Sidebar from "./components/Sidebar.jsx";

const newSessionId = () => `ui-${crypto.randomUUID().replaceAll("-", "")}`;

export default function App() {
  const [tab, setTab] = useState("chat");
  const [config, setConfig] = useState(null);
  const [configError, setConfigError] = useState(null);
  const [provider, setProvider] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(newSessionId);

  useEffect(() => {
    getConfig()
      .then((cfg) => {
        setConfig(cfg);
        setProvider(cfg.default_provider);
      })
      .catch((err) => setConfigError(err.message));
  }, []);

  const clearChat = () => {
    setMessages([]);
    setSessionId(newSessionId());
  };

  return (
    <div className="app">
      <header className="tabs">
        <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>
          🏠 Trading Assistant
        </button>
        <button className={tab === "docs" ? "active" : ""} onClick={() => setTab("docs")}>
          📚 Documentation
        </button>
      </header>

      {tab === "chat" ? (
        <div className="layout">
          <Sidebar
            config={config}
            provider={provider}
            onProviderChange={setProvider}
            onClear={clearChat}
          />
          <main className="main">
            <h1>Trading Assistant Chatbox</h1>
            {configError && <div className="error">Cannot reach the API: {configError}</div>}
            <Chat
              messages={messages}
              setMessages={setMessages}
              sessionId={sessionId}
              provider={provider}
              disabled={!config}
            />
          </main>
        </div>
      ) : (
        <Docs />
      )}
    </div>
  );
}
