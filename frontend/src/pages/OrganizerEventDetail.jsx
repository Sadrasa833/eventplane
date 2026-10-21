import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorBanner, StatusPill } from "../components/Ui";

const NEXT_STATUS = {
  draft: "published",
  published: "closed",
  closed: "finished",
  finished: null,
};

function StatusControl({ event, onChanged }) {
  const [error, setError] = useState("");
  const next = NEXT_STATUS[event.status];

  async function advance() {
    setError("");
    try {
      await api.patch(`organizer/events/${event.id}/status/`, { status: next });
      onChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} />
      {next ? (
        <button onClick={advance}>
          Move to “{next}”
        </button>
      ) : (
        <p className="muted">Final state reached.</p>
      )}
    </div>
  );
}

function StagesPanel({ eventId, stages, onChanged }) {
  const [form, setForm] = useState({ title: "", order: stages.length + 1, start_time: "", end_time: "" });
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post(`organizer/events/${eventId}/stages/`, {
        ...form,
        order: Number(form.order),
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
      });
      setForm({ title: "", order: stages.length + 2, start_time: "", end_time: "" });
      onChanged();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Stages</h2>
      <ul>
        {stages.map((s) => (
          <li key={s.id}>
            {s.order}. {s.title} — {new Date(s.start_time).toLocaleString()} →{" "}
            {new Date(s.end_time).toLocaleString()}
          </li>
        ))}
      </ul>
      <form onSubmit={submit} className="inline-form">
        <ErrorBanner message={error} />
        <input
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          required
        />
        <input
          type="number"
          min="1"
          placeholder="Order"
          value={form.order}
          onChange={(e) => setForm((f) => ({ ...f, order: e.target.value }))}
          required
        />
        <input
          type="datetime-local"
          value={form.start_time}
          onChange={(e) => setForm((f) => ({ ...f, start_time: e.target.value }))}
          required
        />
        <input
          type="datetime-local"
          value={form.end_time}
          onChange={(e) => setForm((f) => ({ ...f, end_time: e.target.value }))}
          required
        />
        <button type="submit">Add stage</button>
      </form>
    </section>
  );
}

function AttributesPanel({ eventId }) {
  const [definitions, setDefinitions] = useState([]);
  const [values, setValues] = useState([]);
  const [defForm, setDefForm] = useState({ key: "", label: "", value_type: "text", applies_to: "event" });
  const [valueForm, setValueForm] = useState({ attribute: "", input_value: "" });
  const [error, setError] = useState("");

  function loadAll() {
    api.get("attribute-definitions/").then((d) => setDefinitions(d.results ?? d));
    api
      .get(`organizer/events/${eventId}/attributes/`)
      .then((d) => setValues(d.results ?? d))
      .catch(() => setValues([]));
  }

  useEffect(loadAll, [eventId]);

  async function createDefinition(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("attribute-definitions/", defForm);
      setDefForm({ key: "", label: "", value_type: "text", applies_to: "event" });
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  }

  async function setValue(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post(`organizer/events/${eventId}/attributes/`, {
        attribute: Number(valueForm.attribute),
        input_value: valueForm.input_value,
      });
      setValueForm({ attribute: "", input_value: "" });
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  }

  const eventDefs = definitions.filter((d) => d.applies_to === "event");

  return (
    <section className="card">
      <h2>Dynamic attributes</h2>
      <ErrorBanner message={error} />

      <h3>Values on this event</h3>
      <ul>
        {values.map((v) => (
          <li key={v.id}>
            <strong>{v.attribute_key}</strong>: {String(v.value)}
          </li>
        ))}
        {values.length === 0 && <li className="muted">No attribute values set yet.</li>}
      </ul>

      <form onSubmit={setValue} className="inline-form">
        <select
          value={valueForm.attribute}
          onChange={(e) => setValueForm((f) => ({ ...f, attribute: e.target.value }))}
          required
        >
          <option value="">Select attribute…</option>
          {eventDefs.map((d) => (
            <option key={d.id} value={d.id}>
              {d.label} ({d.value_type})
            </option>
          ))}
        </select>
        <input
          placeholder="Value"
          value={valueForm.input_value}
          onChange={(e) => setValueForm((f) => ({ ...f, input_value: e.target.value }))}
          required
        />
        <button type="submit">Set value</button>
      </form>

      <details>
        <summary>Define a new attribute (shared across events)</summary>
        <form onSubmit={createDefinition} className="inline-form">
          <input
            placeholder="key (e.g. difficulty_level)"
            value={defForm.key}
            onChange={(e) => setDefForm((f) => ({ ...f, key: e.target.value }))}
            required
          />
          <input
            placeholder="Label"
            value={defForm.label}
            onChange={(e) => setDefForm((f) => ({ ...f, label: e.target.value }))}
            required
          />
          <select
            value={defForm.value_type}
            onChange={(e) => setDefForm((f) => ({ ...f, value_type: e.target.value }))}
          >
            <option value="text">Text</option>
            <option value="number">Number</option>
            <option value="boolean">Boolean</option>
            <option value="date">Date</option>
          </select>
          <select
            value={defForm.applies_to}
            onChange={(e) => setDefForm((f) => ({ ...f, applies_to: e.target.value }))}
          >
            <option value="event">Event</option>
            <option value="stage">Stage</option>
          </select>
          <button type="submit">Create definition</button>
        </form>
      </details>
    </section>
  );
}

function ParticipantsPanel({ eventId }) {
  const [participants, setParticipants] = useState([]);

  useEffect(() => {
    api
      .get(`organizer/events/${eventId}/participants/`)
      .then((d) => setParticipants(d.results ?? d))
      .catch(() => setParticipants([]));
  }, [eventId]);

  return (
    <section className="card">
      <h2>Participants ({participants.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Status</th>
            <th>Registered</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((p) => (
            <tr key={p.id}>
              <td>{p.participant_username}</td>
              <td>{p.participant_email}</td>
              <td>{p.status}</td>
              <td>{new Date(p.registered_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function FeedbackPanel({ eventId, isFinished }) {
  const [feedback, setFeedback] = useState([]);

  useEffect(() => {
    if (!isFinished) return;
    api
      .get(`organizer/events/${eventId}/feedback/`)
      .then((d) => setFeedback(d.results ?? d))
      .catch(() => setFeedback([]));
  }, [eventId, isFinished]);

  if (!isFinished) return null;

  return (
    <section className="card">
      <h2>Feedback</h2>
      {feedback.length === 0 && <p className="muted">No feedback yet.</p>}
      <ul>
        {feedback.map((f) => (
          <li key={f.id}>
            Rating {f.rating}/5 — {f.comment || <span className="muted">(no comment)</span>}
          </li>
        ))}
      </ul>
    </section>
  );
}

function ResultsPanel({ eventId, isFinished, participants }) {
  const [summary, setSummary] = useState("");
  const [entries, setEntries] = useState([{ participant: "", rank: 1, score: "", details: "" }]);
  const [error, setError] = useState("");
  const [published, setPublished] = useState(null);

  useEffect(() => {
    if (!isFinished) return;
    api
      .get(`public/events/${eventId}/results/`)
      .then(setPublished)
      .catch(() => setPublished(null));
  }, [eventId, isFinished]);

  if (!isFinished) return null;

  function updateEntry(i, field, value) {
    setEntries((es) => es.map((e, idx) => (idx === i ? { ...e, [field]: value } : e)));
  }

  function addEntry() {
    setEntries((es) => [...es, { participant: "", rank: es.length + 1, score: "", details: "" }]);
  }

  async function publish(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post(`organizer/events/${eventId}/results/`, {
        summary,
        entries: entries.map((en) => ({
          participant: Number(en.participant),
          rank: Number(en.rank),
          score: en.score,
          details: en.details,
        })),
      });
      const data = await api.get(`public/events/${eventId}/results/`);
      setPublished(data);
    } catch (err) {
      setError(err.message);
    }
  }

  if (published) {
    return (
      <section className="card">
        <h2>Results (published)</h2>
        <p>{published.summary}</p>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Participant</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {published.entries.map((en) => (
              <tr key={en.id}>
                <td>{en.rank}</td>
                <td>{en.participant_username}</td>
                <td>{en.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Publish results</h2>
      <ErrorBanner message={error} />
      <form onSubmit={publish}>
        <label>
          Summary
          <input value={summary} onChange={(e) => setSummary(e.target.value)} />
        </label>
        {entries.map((en, i) => (
          <div key={i} className="inline-form">
            <select value={en.participant} onChange={(e) => updateEntry(i, "participant", e.target.value)} required>
              <option value="">Participant…</option>
              {participants.map((p) => (
                <option key={p.participant} value={p.participant}>
                  {p.participant_username}
                </option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Rank"
              value={en.rank}
              onChange={(e) => updateEntry(i, "rank", e.target.value)}
              required
            />
            <input
              placeholder="Score"
              value={en.score}
              onChange={(e) => updateEntry(i, "score", e.target.value)}
            />
            <input
              placeholder="Details"
              value={en.details}
              onChange={(e) => updateEntry(i, "details", e.target.value)}
            />
          </div>
        ))}
        <button type="button" onClick={addEntry}>
          + Add row
        </button>
        <button type="submit">Publish results</button>
      </form>
    </section>
  );
}

export default function OrganizerEventDetail() {
  const { id } = useParams();
  const [event, setEvent] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [error, setError] = useState("");

  function load() {
    api.get(`organizer/events/${id}/`).then(setEvent).catch((err) => setError(err.message));
    api
      .get(`organizer/events/${id}/participants/`)
      .then((d) => setParticipants(d.results ?? d))
      .catch(() => setParticipants([]));
  }

  useEffect(load, [id]);

  if (error) return <ErrorBanner message={error} />;
  if (!event) return <p>Loading…</p>;

  const isFinished = event.status === "finished";

  return (
    <div>
      <h1>
        {event.title} <StatusPill status={event.status} />
      </h1>
      <p>{event.description}</p>
      <StatusControl event={event} onChanged={load} />

      <StagesPanel eventId={event.id} stages={event.stages} onChanged={load} />
      <AttributesPanel eventId={event.id} />
      <ParticipantsPanel eventId={event.id} />
      <FeedbackPanel eventId={event.id} isFinished={isFinished} />
      <ResultsPanel eventId={event.id} isFinished={isFinished} participants={participants} />
    </div>
  );
}
