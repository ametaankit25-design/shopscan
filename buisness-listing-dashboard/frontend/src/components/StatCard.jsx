// src/components/StatCard.jsx

export default function StatCard({ icon, iconClass = 'blue', value, label }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${iconClass}`}>{icon}</div>
      <div className="stat-body">
        <div className="stat-value">{value?.toLocaleString() ?? '—'}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}
