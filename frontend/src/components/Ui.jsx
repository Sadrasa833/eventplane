export function StatusPill({ status }) {
  return <span className={`pill pill-${status}`}>{status}</span>;
}

export function ErrorBanner({ message }) {
  if (!message) return null;
  return <div className="error-banner">{message}</div>;
}
