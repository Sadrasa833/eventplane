import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { ErrorBanner, StatusPill } from "../components/Ui";

export default function EventDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [event, setEvent] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.get(`public/events/${id}/`).then(setEvent).catch((err) => setError(err.message));
    api
      .get(`public/events/${id}/results/`)
      .then(setResults)
      .catch(() => setResults(null));
  }, [id]);

  async function handleRegister() {
    setError("");
    setMessage("");
    try {
      await api.post("registrations/", { event: Number(id) });
      setMessage("Registered successfully!");
      const updated = await api.get(`public/events/${id}/`);
      setEvent(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  if (error && !event) return <ErrorBanner message={error} />;
  if (!event) return <p>Loading…</p>;

  return (
    <div className="card">
      <h1>
        {event.title} <StatusPill status={event.status} />
      </h1>
      <p className="muted">
        {new Date(event.start_time).toLocaleString()} → {new Date(event.end_time).toLocaleString()}
      </p>
      <p>{event.description}</p>
      <p className="muted">{event.spots_left} spot(s) left</p>

      <ErrorBanner message={error} />
      {message && <p className="success-banner">{message}</p>}

      {user?.role === "participant" && (
        <button onClick={handleRegister} disabled={event.spots_left <= 0}>
          {event.spots_left <= 0 ? "Full" : "Register"}
        </button>
      )}
      {!user && <p className="muted">Log in as a participant to register.</p>}

      {event.stages?.length > 0 && (
        <>
          <h2>Stages</h2>
          <ul>
            {event.stages.map((s) => (
              <li key={s.id}>
                <strong>{s.order}. {s.title}</strong> —{" "}
                {new Date(s.start_time).toLocaleString()} → {new Date(s.end_time).toLocaleString()}
              </li>
            ))}
          </ul>
        </>
      )}

      {results && (
        <>
          <h2>Results</h2>
          {results.summary && <p>{results.summary}</p>}
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Participant</th>
                <th>Score</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {results.entries.map((e) => (
                <tr key={e.id}>
                  <td>{e.rank}</td>
                  <td>{e.participant_username}</td>
                  <td>{e.score}</td>
                  <td>{e.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
