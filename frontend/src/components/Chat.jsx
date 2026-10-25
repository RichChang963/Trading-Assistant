import { useEffect, useRef, useState } from "react";
import { sendChat } from "../api.js";
import Markdown from "./Markdown.jsx";

export default function Chat({
  messages,
  setMessages,
  sessionId,
  provider,
  model,
  examples,
  disabled,
}) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const send = async (raw) => {
    const text = raw.trim();
    if (!text || loading || disabled) return;

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
      inputRef.current?.focus();
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    send(input);
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <section className="chat-card">
      <header className="chat-head">
        <div className="chat-title">
          <span className={`status-dot${disabled ? " off" : ""}`} />
          Market Analyst
        </div>
        <div className="chat-meta">
          {provider && <span className="chip">{provider}</span>}
          {model && <span className="chip muted">{model}</span>}
        </div>
      </header>

      <div className="messages">
        {messages.length === 0 && !loading ? (
          <div className="empty">
            <h1>
              Ask about <span className="gradient-text">markets</span>
            </h1>
            <p>Stocks, commodities and economic indicators, analyzed from live data.</p>
            <div className="examples">
              {examples.map((q) => (
                <button key={q} className="example" onClick={() => send(q)} disabled={disabled}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`message ${m.role}${m.isError ? " is-error" : ""}`}>
              <div className="avatar">{m.role === "user" ? "You" : "AI"}</div>
              <div className="bubble">
                <Markdown>{m.content}</Markdown>
                {m.rawData && (
                  <details className="raw">
                    <summary>View raw data</summary>
                    <pre>{m.rawData}</pre>
                  </details>
                )}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message assistant">
            <div className="avatar">AI</div>
            <div className="bubble typing" aria-label="Processing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={onSubmit}>
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask about stocks, markets, or economic data..."
          disabled={disabled || loading}
        />
        <button className="btn primary" type="submit" disabled={disabled || loading || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
