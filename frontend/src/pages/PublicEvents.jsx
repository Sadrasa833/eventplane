import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ErrorBanner } from "../components/Ui";

export default function PublicEvents() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("public/events/")
      .then((data) => setEvents(data.results ?? data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading events…</p>;

  return (
    <div>
      <h1>Published events</h1>
      <ErrorBanner message={error} />
      {events.length === 0 && <p>No published events yet.</p>}
      <div className="grid">
        {events.map((ev) => (
          <Link to={`/events/${ev.id}`} key={ev.id} className="card event-card">
            <h2>{ev.title}</h2>
            <p className="muted">
              {new Date(ev.start_time).toLocaleString()} → {new Date(ev.end_time).toLocaleString()}
            </p>
            <p>{ev.description}</p>
            <p className="muted">{ev.spots_left} spot(s) left</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
