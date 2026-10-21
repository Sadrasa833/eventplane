import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="nav">
        <Link to="/" className="brand">
          Event Planet
        </Link>
        <nav>
          <Link to="/">Events</Link>
          {user?.role === "participant" && <Link to="/my-registrations">My registrations</Link>}
          {user?.role === "organizer" && <Link to="/organizer">My events</Link>}
          {!user && <Link to="/login">Login</Link>}
          {!user && <Link to="/register">Register</Link>}
          {user && (
            <>
              <span className="user-chip">
                {user.username} · {user.role}
              </span>
              <button className="link-btn" onClick={handleLogout}>
                Logout
              </button>
            </>
          )}
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
