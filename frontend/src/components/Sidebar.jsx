export default function Sidebar({ config, provider, onProviderChange, onClear }) {
  const current = config?.providers.find((p) => p.id === provider);

  return (
    <aside className="sidebar">
      <h2>⚙️ Settings</h2>

      <h3>🤖 Agent Mode</h3>
      <div className="info">
        📡 <b>Data Agent</b> fetches data
        <br />
        <br />
        📊 <b>Analysis Agent</b> provides insights
      </div>

      <label htmlFor="provider">Select Model Provider</label>
      <select
        id="provider"
        value={provider}
        onChange={(e) => onProviderChange(e.target.value)}
        disabled={!config}
      >
        {config?.providers.map((p) => (
          <option key={p.id} value={p.id}>
            {p.id}
          </option>
        ))}
      </select>
      {current && (
        <div className="info">
          <b>Model:</b> {current.model}
        </div>
      )}

      <h3>Chat Controls</h3>
      <button className="wide" onClick={onClear}>
        🗑️ Clear Chat History
      </button>

      <hr />
      <h3>Data Sources</h3>
      <p>OpenBB (using Yahoo Finance &amp; OECD as two main sources)</p>

      <h3>Example questions</h3>
      <ul>
        {config?.example_questions.map((q) => (
          <li key={q}>{q}</li>
        ))}
      </ul>
    </aside>
  );
}
