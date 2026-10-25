import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

let mermaidPromise;
const loadMermaid = () => {
  mermaidPromise ??= import("mermaid").then((m) => {
    m.default.initialize({ startOnLoad: false, theme: "default", securityLevel: "strict" });
    return m.default;
  });
  return mermaidPromise;
};

let diagramCount = 0;

function Mermaid({ code }) {
  const ref = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    loadMermaid()
      .then((mermaid) => mermaid.render(`mermaid-${diagramCount++}`, code))
      .then(({ svg }) => {
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      })
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [code]);

  if (error) return <pre>{code}</pre>;
  return <div ref={ref} className="mermaid" />;
}

const components = {
  code({ className, children, ...props }) {
    if (/language-mermaid/.test(className ?? "")) {
      return <Mermaid code={String(children).trim()} />;
    }
    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

export default function Markdown({ children }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {children}
    </ReactMarkdown>
  );
}
