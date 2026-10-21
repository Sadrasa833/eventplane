# Event Planet

API-first event planning & management platform — Django + Django REST
Framework + PostgreSQL, containerized with Docker.

## Quick start

```bash
cp .env.example .env      # edit values if you want, defaults work out of the box
docker compose up --build
```

The API is then available at `http://localhost:8000/api/`.

Required env vars (see `.env.example`): `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
`DJANGO_ALLOWED_HOSTS`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_PORT`. The `web` service waits for Postgres to be healthy, then
runs migrations automatically before starting Gunicorn.

Create a superuser (for `/admin/`) after the containers are up:

```bash
docker compose exec web python manage.py createsuperuser
```

## Architecture decisions

The spec deliberately leaves two design choices open. This project resolves
them as follows:

1. **Registration is at the Event level, not per-Stage.** A participant
   registers once for an event and that covers all of its stages. Stages
   are used to structure the event's schedule and to attach stage-specific
   roles (speaker/judge/mentor), not as separate registration units. This
   keeps a single, simple capacity/registration model that still works for
   multi-stage events (workshops with several sessions, multi-round
   tournaments, etc.).
2. **Capacity is checked at the Event level**, for the same reason —
   `Event.capacity` and `Event.confirmed_registration_count` are the single
   source of truth. If a future event type needed per-stage capacity, the
   `Stage` model already has an isolated migration path since it currently
   holds no capacity field.

### Dynamic attributes (EAV)

- `AttributeDefinition` — the reusable, independent metadata: `key`,
  `label`, `value_type` (text/number/boolean/date), `applies_to`
  (event/stage). One definition can be shared across many events.
- `AttributeValue` — the concrete value for one specific Event or Stage
  (via a `GenericForeignKey`, restricted in `clean()` to those two models).
  Exactly one of four typed columns (`value_text`, `value_number`,
  `value_boolean`, `value_date`) is populated — no `JSONField`, no new
  column per attribute, and the value is always type-safe.

### Event lifecycle

`Event.ALLOWED_TRANSITIONS` enforces a forward-only state machine:
`Draft → Published → Closed → Finished`. Any other transition (including
skipping a step or going backward) raises a validation error, both from
`Event.transition_to()` and from the `PATCH .../status/` endpoint.

### Results

`Result`/`ResultEntry` are a single, event-type-agnostic model
(participant + rank + score + free-text details) rather than a schema per
event type — this covers tournaments, webinars, workshops and sports
events without extra tables, at the cost of not modeling type-specific
result data (e.g. a tournament bracket) beyond free text.

## API map

**Auth** (`/api/auth/`)
- `POST register/` — sign up as `organizer` or `participant`
- `POST login/` — get a token
- `GET me/` — current user

**Public** (no auth)
- `GET /api/public/events/` — Published events only
- `GET /api/public/events/{id}/`
- `GET /api/public/events/{event_id}/results/` — published results only

**Participant** (token auth)
- `POST /api/registrations/` — register for a Published event
- `GET /api/registrations/` — your own registrations
- `POST /api/feedback/` — feedback on a Finished event you registered for

**Organizer** (token auth, role=organizer, object-level ownership checks)
- `GET/POST /api/organizer/events/` , `GET/PUT/PATCH/DELETE .../{id}/`
- `PATCH /api/organizer/events/{id}/status/` — lifecycle transition
- `GET/POST /api/organizer/events/{event_id}/stages/`, `.../{id}/`
- `GET/POST /api/organizer/stages/{stage_id}/roles/` — speaker/judge/mentor
- `GET/POST /api/organizer/events/{event_id}/attributes/` — attribute values
- `GET /api/organizer/events/{event_id}/participants/`
- `GET /api/organizer/events/{event_id}/feedback/`
- `POST /api/organizer/events/{event_id}/results/` — publish results

**Attribute definitions** (`/api/attribute-definitions/`) — readable by
anyone, writable by organizers only.

All protected endpoints require `Authorization: Token <token>`.

## UI (optional, included)

A separate React frontend lives in `frontend/` (Vite + React Router,
plain `fetch`). It only consumes the API — no business logic lives in
the frontend; every rule (capacity, duplicate registration, status
transitions, feedback timing, etc.) is enforced server-side and the UI
just surfaces whatever error the API returns.

**Run everything together:**

```bash
docker compose up --build
```

This starts Postgres, the Django API on `:8000`, and the built frontend
(served by nginx) on `:5173`. `CORS_ALLOWED_ORIGINS` (backend) and
`FRONTEND_API_BASE_URL` (frontend, baked in at build time) already point
at each other by default — override both in `.env` if you change ports.

**Run the frontend alone, against a local API, for development:**

```bash
cd frontend
cp .env.example .env     # VITE_API_BASE_URL, defaults to http://localhost:8000/api
npm install
npm run dev               # http://localhost:5173, hot-reloading
```

**What it covers:**
- Register / login (choose Organizer or Participant), token stored in
  `localStorage`.
- Public: browse Published events, view an event's stages and (once
  Finished) its published results.
- Participant: register for an event, view own registrations, submit
  feedback once an event is Finished.
- Organizer: create events (start as Draft), advance status along the
  legal state machine, manage stages, define/set dynamic attributes,
  view the participant list, view feedback, and publish results.

`frontend/` structure:

```
src/api/client.js        thin fetch wrapper (auth header, error handling) — no logic
src/context/AuthContext  current user/token
src/pages/                one file per screen
src/components/           nav layout, route guard, small UI helpers
```

## Project layout

```
accounts/        custom User model (role: organizer/participant), auth endpoints
events/          Event, Stage, StageRoleAssignment, lifecycle state machine
attributes/      EAV: AttributeDefinition, AttributeValue
registrations/   Registration (capacity + duplicate checks)
feedback/        Feedback, Result, ResultEntry
config/          settings, root urls, wsgi
frontend/        optional React UI (Vite + React Router), API-only
```

## Notes

- Tested end-to-end against SQLite via Django's test client during
  development (register → create/publish event → attributes → stages →
  register/duplicate/capacity checks → lifecycle transitions → feedback →
  results). The Docker/Postgres path follows the same code path and
  standard `docker-compose` patterns, but wasn't run through an actual
  Docker daemon in the environment this was built in — sanity-check
  `docker compose up --build` once before submitting.
