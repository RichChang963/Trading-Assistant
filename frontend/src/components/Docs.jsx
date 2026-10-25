import { useEffect, useState } from "react";
import { getDoc, listDocs } from "../api.js";
import Markdown from "./Markdown.jsx";

export default function Docs() {
  const [docs, setDocs] = useState([]);
  const [selected, setSelected] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    listDocs()
      .then((items) => {
        setDocs(items);
        if (items.length) setSelected(items[0].id);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selected) return;
    getDoc(selected)
      .then((doc) => setContent(doc.content))
      .catch((err) => setError(err.message));
  }, [selected]);

  return (
    <main className="docs">
      <div className="docs-inner">
        <h1>Documentation</h1>
        {error && <div className="alert">{error}</div>}
        <select value={selected} onChange={(e) => setSelected(e.target.value)} aria-label="Document">
          {docs.map((d) => (
            <option key={d.id} value={d.id}>
              {d.title}
            </option>
          ))}
        </select>
        <article className="doc-body">
          <Markdown>{content}</Markdown>
        </article>
      </div>
    </main>
  );
}
