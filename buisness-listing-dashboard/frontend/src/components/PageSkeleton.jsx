// src/components/PageSkeleton.jsx
// Shimmering placeholder shown while the Dashboard / Analytics stats are loading.
export default function PageSkeleton({ cards = 4, charts = 2 }) {
  return (
    <div className="vazhi-dashboard-page vazhi-container" role="status" aria-label="Loading">
      <div className="skeleton" style={{ height: 36, width: '40%', maxWidth: 340, marginBottom: 12 }} />
      <div className="skeleton" style={{ height: 16, width: '60%', maxWidth: 480, marginBottom: 32 }} />
      {cards > 0 && (
        <div className="stat-grid-4">
          {Array.from({ length: cards }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 98, borderRadius: 12 }} />
          ))}
        </div>
      )}
      <div className="charts-row-2">
        {Array.from({ length: charts }).map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 320, borderRadius: 12 }} />
        ))}
      </div>
    </div>
  );
}
