import { useEffect, useRef, useState } from "react";
import { sendChat } from "../api.js";
import Markdown from "./Markdown.jsx";

export default function Chat({ messages, setMessages, sessionId, provider, disabled }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await sendChat({ message: text, sessionId, provider });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.analysis, rawData: res.raw_data },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}`, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}${m.isError ? " error" : ""}`}>
            <div className="avatar">{m.role === "user" ? "🧑" : "🤖"}</div>
            <div className="bubble">
              <Markdown>{m.content}</Markdown>
              {m.rawData && (
                <details>
                  <summary>📁 View Raw Data</summary>
                  <pre>{m.rawData}</pre>
                </details>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="message assistant"><div className="avatar">🤖</div><div className="bubble">Processing...</div></div>}
        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={submit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about stocks, markets, or economic data..."
          disabled={disabled || loading}
        />
        <button type="submit" disabled={disabled || loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
