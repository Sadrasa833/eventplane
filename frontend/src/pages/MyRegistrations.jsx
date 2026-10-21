import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ErrorBanner, StatusPill } from "../components/Ui";

function FeedbackForm({ registrationId, onDone }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("feedback/", { registration: registrationId, rating: Number(rating), comment });
      setSent(true);
      onDone?.();
    } catch (err) {
      setError(err.message);
    }
  }

  if (sent) return <p className="success-banner">Thanks for your feedback!</p>;

  return (
    <form onSubmit={submit} className="inline-form">
      <ErrorBanner message={error} />
      <label>
        Rating
        <select value={rating} onChange={(e) => setRating(e.target.value)}>
          {[5, 4, 3, 2, 1].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </label>
      <input
        placeholder="Optional comment"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />
      <button type="submit">Send feedback</button>
    </form>
  );
}

export default function MyRegistrations() {
  const [registrations, setRegistrations] = useState([]);
  const [error, setError] = useState("");

  function load() {
    api
      .get("registrations/")
      .then((data) => setRegistrations(data.results ?? data))
      .catch((err) => setError(err.message));
  }

  useEffect(load, []);

  return (
    <div>
      <h1>My registrations</h1>
      <ErrorBanner message={error} />
      {registrations.length === 0 && <p>You haven't registered for any events yet.</p>}
      <div className="grid">
        {registrations.map((r) => (
          <div key={r.id} className="card">
            <h2>
              {r.event_title} <StatusPill status={r.status} />
            </h2>
            <p className="muted">Registered {new Date(r.registered_at).toLocaleString()}</p>
            <FeedbackForm registrationId={r.id} onDone={load} />
          </div>
        ))}
      </div>
    </div>
  );
}
