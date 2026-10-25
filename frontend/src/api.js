async function request(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const getConfig = () => request("/api/config");

export const sendChat = ({ message, sessionId, provider }) =>
  request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId, provider }),
  });

export const listDocs = () => request("/api/docs");

export const getDoc = (id) => request(`/api/docs/${encodeURIComponent(id)}`);
