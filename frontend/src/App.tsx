import { useEffect, useState } from "react";

type Health = { status: string; env: string };

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => (res.ok ? res.json() : Promise.reject(new Error(`HTTP ${res.status}`))))
      .then(setHealth)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 640, margin: "48px auto", padding: "0 16px" }}>
      <h1>Trader Slave</h1>
      <p>
        Stato dell'API:{" "}
        {error ? <strong>non raggiungibile ({error})</strong> : health ? <strong>{health.status} ({health.env})</strong> : "verifica in corso…"}
      </p>
    </main>
  );
}
