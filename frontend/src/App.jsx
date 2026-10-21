import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import RequireRole from "./components/RequireRole";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PublicEvents from "./pages/PublicEvents";
import EventDetail from "./pages/EventDetail";
import MyRegistrations from "./pages/MyRegistrations";
import OrganizerEvents from "./pages/OrganizerEvents";
import OrganizerEventDetail from "./pages/OrganizerEventDetail";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<PublicEvents />} />
        <Route path="/events/:id" element={<EventDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/my-registrations"
          element={
            <RequireRole role="participant">
              <MyRegistrations />
            </RequireRole>
          }
        />
        <Route
          path="/organizer"
          element={
            <RequireRole role="organizer">
              <OrganizerEvents />
            </RequireRole>
          }
        />
        <Route
          path="/organizer/events/:id"
          element={
            <RequireRole role="organizer">
              <OrganizerEventDetail />
            </RequireRole>
          }
        />
      </Route>
    </Routes>
  );
}
