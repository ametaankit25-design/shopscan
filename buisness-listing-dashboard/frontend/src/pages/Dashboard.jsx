// src/pages/Dashboard.jsx
import { useEffect, useState } from 'react';
import { Building2, MapPin, Tag, Zap, TrendingUp, BarChart3, PieChart as PieIcon } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
  fetchStatsOverview,
  fetchStatsByCategory,
  fetchStatsByCity,
  fetchStatsBySource,
  describeApiError,
} from '../api/client';
import ErrorState from '../components/ErrorState';
import PageSkeleton from '../components/PageSkeleton';
import useCountUp from '../utils/useCountUp';

function AnimatedValue({ value }) {
  const shown = useCountUp(value);
  return <>{shown?.toLocaleString() ?? '—'}</>;
}

const STAT_CARDS = [
  { key: 'total_listings', label: 'Total Listings', Icon: Building2, style: undefined },
  { key: 'total_cities', label: 'Destinations Covered', Icon: MapPin, style: { background: '#edf5ef', color: '#2f6b4f' } },
  { key: 'total_categories', label: 'Active Categories', Icon: Tag, style: { background: '#edf5ef', color: '#2f6b4f' } },
  { key: 'total_sources', label: 'Data Sources', Icon: Zap, style: { background: '#f7f1dc', color: '#9a7b1c' } },
];

const PIE_COLORS = [
  '#7a1f2b', '#2f6b4f', '#5f8f73', '#c9a227',
  '#9c4a57', '#8fb59b', '#b0785d', '#d8b56a',
];

const CustomTooltip = ({ active, payload, label }) => {
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
      <div style={{ color: '#64748b', marginBottom: 2 }}>{label}</div>
      <strong>{payload[0].value?.toLocaleString()}</strong> listings
    </div>
  );
};

const PieCustomTooltip = ({ active, payload }) => {
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
      <div style={{ color: '#64748b', marginBottom: 2 }}>{payload[0].name}</div>
      <strong>{payload[0].value?.toLocaleString()}</strong>
    </div>
  );
};

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetchStatsOverview(),
      fetchStatsByCategory(8),
      fetchStatsByCity(8),
      fetchStatsBySource(),
    ]).then(([ov, cat, cit, src]) => {
      if (cancelled) return;
      setOverview(ov);
      setCategories(cat);
      setCities(cit);
      setSources(src);
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
    return <PageSkeleton />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={retry} />;
  }

  if (!overview?.total_listings) {
    return (
      <ErrorState
        title="No listings yet"
        message="The database is empty. Load data with: python scripts/scrape_directory.py"
        onRetry={retry}
      />
    );
  }

  return (
    <div className="vazhi-dashboard-page vazhi-container page-enter">
      <div style={{ marginBottom: 32 }}>
        <h1 className="dashboard-hero-title">Directory Intelligence & Metrics</h1>
        <p className="dashboard-hero-subtitle">
          Real-time aggregations from all database listings, locations, and source integrations.
        </p>
      </div>

      {/* Overview Stat Cards */}
      <div className="stat-grid-4">
        {STAT_CARDS.map(({ key, label, Icon, style }, i) => (
          <div key={key} className="stat-card-vazhi stagger-item" style={{ '--i': i }}>
            <div className="stat-icon-wrap" style={style}><Icon size={24} /></div>
            <div>
              <div className="stat-vazhi-value"><AnimatedValue value={overview?.[key]} /></div>
              <div className="stat-vazhi-label">{label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="charts-row-2">
        {/* Category Bar Chart */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 4 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Top Categories</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Listings by classification</p>
            </div>
            <TrendingUp size={18} color="#7a1f2b" />
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={categories} margin={{ left: -15, bottom: 25 }}>
              <XAxis
                dataKey="label"
                tick={{ fill: '#64748b', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                interval={0}
                angle={-25}
                textAnchor="end"
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#7a1f2b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Source Pie Chart */}
        <div className="chart-card-vazhi stagger-item" style={{ '--i': 5 }}>
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Data Origin</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Distribution by ingestion source</p>
            </div>
            <PieIcon size={18} color="#7a1f2b" />
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <text x="50%" y="44%" textAnchor="middle" dominantBaseline="central"
                style={{ fontSize: 24, fontWeight: 800, fill: '#1e293b' }}>
                {overview.total_listings.toLocaleString()}
              </text>
              <text x="50%" y="54%" textAnchor="middle" dominantBaseline="central"
                style={{ fontSize: 11, fill: '#64748b' }}>
                listings
              </text>
              <Pie
                data={sources}
                dataKey="count"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
                animationDuration={900}
                animationEasing="ease-out"
              >
                {sources.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<PieCustomTooltip />} />
              <Legend
                formatter={(value) => (
                  <span style={{ color: '#4b5563', fontSize: '0.76rem', fontWeight: 500 }}>{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cities Bar Chart */}
      <div className="chart-card-vazhi stagger-item" style={{ marginTop: 24, '--i': 6 }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">Listings by Destination City</h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Coverage across top metropolitan hubs</p>
          </div>
          <BarChart3 size={18} color="#7a1f2b" />
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={cities} margin={{ left: -15, bottom: 25 }}>
            <XAxis
              dataKey="label"
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              interval={0}
              angle={-30}
              textAnchor="end"
            />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {cities.map((_, i) => (
                <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
