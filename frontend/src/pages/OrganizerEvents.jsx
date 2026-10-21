import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ErrorBanner, StatusPill } from "../components/Ui";

function CreateEventForm({ onCreated }) {
  const [form, setForm] = useState({
    title: "",
    description: "",
    start_time: "",
    end_time: "",
    capacity: 10,
  });
  const [error, setError] = useState("");

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("organizer/events/", {
        ...form,
        capacity: Number(form.capacity),
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
      });
      setForm({ title: "", description: "", start_time: "", end_time: "", capacity: 10 });
      onCreated();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={submit} className="card">
      <h2>Create event</h2>
      <ErrorBanner message={error} />
      <label>
        Title
        <input value={form.title} onChange={(e) => set("title", e.target.value)} required />
      </label>
      <label>
        Description
        <textarea value={form.description} onChange={(e) => set("description", e.target.value)} />
      </label>
      <label>
        Start time
        <input
          type="datetime-local"
          value={form.start_time}
          onChange={(e) => set("start_time", e.target.value)}
          required
        />
      </label>
      <label>
        End time
        <input
          type="datetime-local"
          value={form.end_time}
          onChange={(e) => set("end_time", e.target.value)}
          required
        />
      </label>
      <label>
        Capacity
        <input
          type="number"
          min="1"
          value={form.capacity}
          onChange={(e) => set("capacity", e.target.value)}
          required
        />
      </label>
      <button type="submit">Create (as Draft)</button>
    </form>
  );
}

export default function OrganizerEvents() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");

  function load() {
    api
      .get("organizer/events/")
      .then((data) => setEvents(data.results ?? data))
      .catch((err) => setError(err.message));
  }

  useEffect(load, []);

  return (
    <div>
      <h1>My events</h1>
      <ErrorBanner message={error} />
      <CreateEventForm onCreated={load} />
      <div className="grid">
        {events.map((ev) => (
          <Link to={`/organizer/events/${ev.id}`} key={ev.id} className="card event-card">
            <h2>
              {ev.title} <StatusPill status={ev.status} />
            </h2>
            <p className="muted">
              {new Date(ev.start_time).toLocaleString()} → {new Date(ev.end_time).toLocaleString()}
            </p>
            <p className="muted">Capacity: {ev.capacity}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
