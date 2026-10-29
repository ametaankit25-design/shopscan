// src/pages/Analytics.jsx
import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area, CartesianGrid,
} from 'recharts';
import {
  fetchStatsByCategory,
  fetchStatsByCity,
  fetchStatsBySource,
  fetchStatsTimeline,
  fetchStatsCityCategory,
  describeApiError,
} from '../api/client';
import ErrorState from '../components/ErrorState';
import PageSkeleton from '../components/PageSkeleton';

const COLORS = [
  '#7a1f2b', '#2f6b4f', '#5f8f73', '#c9a227',
  '#9c4a57', '#8fb59b', '#b0785d', '#d8b56a',
  '#4b1a21', '#355f46',
];
const OTHER_COLOR = '#cbd5e1';

const TooltipBox = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e2e8f0',
      borderRadius: '8px',
      padding: '8px 12px',
      fontSize: '0.82rem',
      color: '#1e293b',
      boxShadow: '0 4px 14px rgba(0,0,0,0.08)',
    }}>
      <div style={{ color: '#64748b', marginBottom: 2 }}>{label ?? payload[0].name}</div>
      {payload.length === 1 ? (
        <><strong>{payload[0].value?.toLocaleString()}</strong> listings</>
      ) : (
        payload.filter((p) => p.value).map((p) => (
          <div key={p.dataKey} style={{ display: 'flex', justifyContent: 'space-between', gap: 16 }}>
            <span style={{ color: p.color }}>{p.name}</span>
            <strong>{p.value}</strong>
          </div>
        ))
      )}
    </div>
  );
};

const shortDate = (iso) => {
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};

export default function Analytics() {
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);
  const [sources, setSources] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [matrix, setMatrix] = useState({ categories: [], rows: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchStatsByCategory(15),
      fetchStatsByCity(15),
      fetchStatsBySource(),
      fetchStatsTimeline(30),
      fetchStatsCityCategory(8, 6),
    ]).then(([cat, cit, src, tl, mx]) => {
      if (cancelled) return;
      setCategories(cat);
      setCities(cit);
      setSources(src);
      setTimeline(tl);
      setMatrix(mx);
    }).catch((err) => {
      if (!cancelled) setError(describeApiError(err));
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, [reloadKey]);

  const retry = () => {
    setLoading(true);
    setError(null);
    setReloadKey((k) => k + 1);
  };

  if (loading) {
    return <PageSkeleton cards={0} charts={4} />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={retry} />;
  }

  if (!sources.length) {
    return (
      <ErrorState
        title="No listings yet"
        message="The database is empty. Load data with: python scripts/scrape_directory.py"
        onRetry={retry}
      />
    );
  }

  const totalListings = sources.reduce((sum, s) => sum + s.count, 0);
  const categoryShare = categories.slice(0, 6);
  const otherCategories = categories.slice(6).reduce((sum, c) => sum + c.count, 0);
  if (otherCategories > 0) categoryShare.push({ label: 'Other', count: otherCategories });
  const addedLast30 = timeline.reduce((sum, p) => sum + p.count, 0);
  const matrixColor = (name, i) => (name === 'Other' ? OTHER_COLOR : COLORS[i % COLORS.length]);

  return (
    <div className="vazhi-dashboard-page vazhi-container page-enter">
      <div style={{ marginBottom: 32 }}>
        <h1 className="dashboard-hero-title">Directory Analytics</h1>
        <p className="dashboard-hero-subtitle">
          In-depth ranking by category volume, metropolitan concentration, growth and ingestion feeds.
        </p>
      </div>

      {/* Category – Horizontal Bar */}
      <div className="chart-card-vazhi stagger-item" style={{ marginBottom: 28, '--i': 0 }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">Category Ranking</h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Top 15 business categories by total listing count</p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={categories} layout="vertical" margin={{ left: 30, right: 20 }}>
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis
              type="category"
              dataKey="label"
              width={110}
              tick={{ fill: '#475569', fontSize: 11, fontWeight: 500 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<TooltipBox />} />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} animationDuration={900}>
              {categories.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* City × Category stacked bars */}
      <div className="chart-card-vazhi stagger-item" style={{ marginBottom: 28, '--i': 1 }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">What Each City Offers</h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Top {matrix.rows.length} cities, split by their leading categories
            </p>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={matrix.rows} margin={{ left: -15, bottom: 10 }}>
            <CartesianGrid vertical={false} stroke="#f1f5f9" />
            <XAxis dataKey="city" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} interval={0} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip content={<TooltipBox />} />
            <Legend
              iconType="circle"
              iconSize={8}
              formatter={(value) => <span style={{ color: '#4b5563', fontSize: '0.76rem' }}>{value}</span>}
            />
            {matrix.categories.map((name, i) => (
              <Bar
                key={name}
                dataKey={name}
                stackId="city"
                fill={matrixColor(name, i)}
                radius={i === matrix.categories.length - 1 ? [4, 4, 0, 0] : 0}
                animationDuration={900}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="charts-row-2">
        {/* Growth timeline */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 2 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Listings Added</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
                {addedLast30.toLocaleString()} new listings in the last 30 days
              </p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={timeline} margin={{ left: -15, right: 10, bottom: 5 }}>
              <defs>
                <linearGradient id="growthFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7a1f2b" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#7a1f2b" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} stroke="#f1f5f9" />
              <XAxis
                dataKey="date"
                tickFormatter={shortDate}
                tick={{ fill: '#64748b', fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                minTickGap={28}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip content={<TooltipBox />} labelFormatter={shortDate} />
              <Area
                type="monotone"
                dataKey="count"
                name="Added"
                stroke="#7a1f2b"
                strokeWidth={2.5}
                fill="url(#growthFill)"
                animationDuration={1100}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Category share */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 3 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Category Share</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Top 6 categories vs. everything else</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={categoryShare}
                dataKey="count"
                nameKey="label"
                cx="50%"
                cy="46%"
                innerRadius={50}
                outerRadius={82}
                paddingAngle={3}
                animationDuration={900}
              >
                {categoryShare.map((entry, i) => (
                  <Cell key={entry.label} fill={entry.label === 'Other' ? OTHER_COLOR : COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<TooltipBox />} />
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(value, entry) => (
                  <span style={{ color: '#4b5563', fontSize: '0.74rem' }}>
                    {value} {totalListings ? `${Math.round((entry.payload.count / totalListings) * 100)}%` : ''}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="charts-row-2">
        {/* City Distribution */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 4 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Destination Coverage</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Top 15 cities with highest directory count</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={Math.max(280, cities.length * 26)}>
            <BarChart data={cities} layout="vertical" margin={{ left: 10, right: 20 }}>
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
              <YAxis
                type="category"
                dataKey="label"
                width={100}
                interval={0}
                tick={{ fill: '#475569', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<TooltipBox />} />
              <Bar dataKey="count" fill="#7a1f2b" radius={[0, 4, 4, 0]} animationDuration={900} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Source Breakdown */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 5 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Feed Source Share</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Share of records by origin channel</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={sources}
                dataKey="count"
                nameKey="label"
                cx="50%"
                cy="46%"
                outerRadius={82}
                animationDuration={900}
              >
                {sources.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<TooltipBox />} />
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(value, entry) => (
                  <span style={{ color: '#4b5563', fontSize: '0.74rem' }}>
                    {value} {totalListings ? `${Math.round((entry.payload.count / totalListings) * 100)}%` : ''}
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Per-city breakdown table */}
      <div className="chart-card-vazhi stagger-item" style={{ marginTop: 28, '--i': 6 }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">City Breakdown</h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Listings per leading category in each top city</p>
          </div>
        </div>
        <div className="analytics-table-wrap">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>City</th>
                {matrix.categories.map((c) => <th key={c}>{c}</th>)}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {matrix.rows.map((row) => {
                const top = matrix.categories
                  .filter((c) => c !== 'Other')
                  .reduce((best, c) => (row[c] > (row[best] ?? -1) ? c : best), null);
                return (
                  <tr key={row.city}>
                    <td className="analytics-table-city">{row.city}</td>
                    {matrix.categories.map((c) => (
                      <td key={c} className={c === top ? 'analytics-table-top' : undefined}>{row[c] || '–'}</td>
                    ))}
                    <td><strong>{row.total}</strong></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
