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
  const [drawerOpen, setDrawerOpen] = useState(false);

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
    setDrawerOpen(false);
  };

  const model = config?.providers.find((p) => p.id === provider)?.model;

  return (
    <div className="app">
      <nav className="navbar">
        {tab === "chat" && (
          <button
            className="icon-btn menu-btn"
            aria-label="Open settings"
            onClick={() => setDrawerOpen(true)}
          >
            ☰
          </button>
        )}
        <div className="brand">
          <span className="brand-mark">📈</span>
          <span className="brand-name">Trading Assistant</span>
        </div>
        <div className="nav-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={tab === "chat"}
            className={tab === "chat" ? "active" : ""}
            onClick={() => setTab("chat")}
          >
            Assistant
          </button>
          <button
            role="tab"
            aria-selected={tab === "docs"}
            className={tab === "docs" ? "active" : ""}
            onClick={() => setTab("docs")}
          >
            Docs
          </button>
        </div>
      </nav>

      {tab === "chat" ? (
        <div className="layout">
          <div
            className={`backdrop${drawerOpen ? " show" : ""}`}
            onClick={() => setDrawerOpen(false)}
          />
          <Sidebar
            open={drawerOpen}
            config={config}
            provider={provider}
            onProviderChange={setProvider}
            onClear={clearChat}
            onClose={() => setDrawerOpen(false)}
          />
          <main className="main">
            {configError && (
              <div className="alert">Cannot reach the API: {configError}</div>
            )}
            <Chat
              messages={messages}
              setMessages={setMessages}
              sessionId={sessionId}
              provider={provider}
              model={model}
              examples={config?.example_questions ?? []}
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
