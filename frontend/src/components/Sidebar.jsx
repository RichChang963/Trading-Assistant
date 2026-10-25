export default function Sidebar({
  open,
  config,
  provider,
  onProviderChange,
  onClear,
  onClose,
}) {
  const current = config?.providers.find((p) => p.id === provider);

  return (
    <aside className={`sidebar${open ? " open" : ""}`}>
      <div className="sidebar-head">
        <h2>Settings</h2>
        <button className="icon-btn close-btn" aria-label="Close settings" onClick={onClose}>
          ✕
        </button>
      </div>

      <section className="panel">
        <h3>Model provider</h3>
        <select
          value={provider}
          onChange={(e) => onProviderChange(e.target.value)}
          disabled={!config}
          aria-label="Model provider"
        >
          {config?.providers.map((p) => (
            <option key={p.id} value={p.id}>
              {p.id}
            </option>
          ))}
        </select>
        {current && <div className="chip model-chip">{current.model || "default model"}</div>}
      </section>

      <section className="panel">
        <h3>How it works</h3>
        <ol className="steps">
          <li>
            <span className="step-dot">1</span>
            <div>
              <b>Route</b>
              <small>Pick the right data tool</small>
            </div>
          </li>
          <li>
            <span className="step-dot">2</span>
            <div>
              <b>Fetch</b>
              <small>OpenBB · Yahoo Finance · OECD</small>
            </div>
          </li>
          <li>
            <span className="step-dot">3</span>
            <div>
              <b>Analyze</b>
              <small>Insights from the retrieved data</small>
            </div>
          </li>
        </ol>
      </section>

      <button className="btn ghost wide" onClick={onClear}>
        🗑️ New conversation
      </button>
    </aside>
  );
}
