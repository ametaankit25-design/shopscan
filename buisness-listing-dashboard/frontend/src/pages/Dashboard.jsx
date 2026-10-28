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
} from '../api/client';

const PIE_COLORS = [
  '#e64942', '#3b82f6', '#10b981', '#f59e0b',
  '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16',
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

  useEffect(() => {
    Promise.all([
      fetchStatsOverview(),
      fetchStatsByCategory(8),
      fetchStatsByCity(8),
      fetchStatsBySource(),
    ]).then(([ov, cat, cit, src]) => {
      setOverview(ov);
      setCategories(cat);
      setCities(cit);
      setSources(src);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="vazhi-container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <p style={{ color: '#858d9d' }}>Loading dashboard insights...</p>
      </div>
    );
  }

  return (
    <div className="vazhi-dashboard-page vazhi-container">
      <div style={{ marginBottom: 32 }}>
        <h1 className="dashboard-hero-title">Directory Intelligence & Metrics</h1>
        <p className="dashboard-hero-subtitle">
          Real-time aggregations from all database listings, locations, and source integrations.
        </p>
      </div>

      {/* Overview Stat Cards */}
      <div className="stat-grid-4">
        <div className="stat-card-vazhi">
          <div className="stat-icon-wrap"><Building2 size={24} /></div>
          <div>
            <div className="stat-vazhi-value">{overview?.total_listings?.toLocaleString() ?? '—'}</div>
            <div className="stat-vazhi-label">Total Listings</div>
          </div>
        </div>

        <div className="stat-card-vazhi">
          <div className="stat-icon-wrap" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            <MapPin size={24} />
          </div>
          <div>
            <div className="stat-vazhi-value">{overview?.total_cities?.toLocaleString() ?? '—'}</div>
            <div className="stat-vazhi-label">Destinations Covered</div>
          </div>
        </div>

        <div className="stat-card-vazhi">
          <div className="stat-icon-wrap" style={{ background: '#eff6ff', color: '#2563eb' }}>
            <Tag size={24} />
          </div>
          <div>
            <div className="stat-vazhi-value">{overview?.total_categories?.toLocaleString() ?? '—'}</div>
            <div className="stat-vazhi-label">Active Categories</div>
          </div>
        </div>

        <div className="stat-card-vazhi">
          <div className="stat-icon-wrap" style={{ background: '#fefce8', color: '#ca8a04' }}>
            <Zap size={24} />
          </div>
          <div>
            <div className="stat-vazhi-value">{overview?.total_sources?.toLocaleString() ?? '—'}</div>
            <div className="stat-vazhi-label">Data Sources</div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-row-2">
        {/* Category Bar Chart */}
        <div className="chart-card-vazhi">
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Top Categories</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Listings by classification</p>
            </div>
            <TrendingUp size={18} color="#e64942" />
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
              <Bar dataKey="count" fill="#e64942" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Source Pie Chart */}
        <div className="chart-card-vazhi">
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Data Origin</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Distribution by ingestion source</p>
            </div>
            <PieIcon size={18} color="#e64942" />
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={sources}
                dataKey="count"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
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
      <div className="chart-card-vazhi" style={{ marginTop: 24 }}>
        <div className="chart-header-row">
          <div>
            <h3 className="chart-title">Listings by Destination City</h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Coverage across top metropolitan hubs</p>
          </div>
          <BarChart3 size={18} color="#e64942" />
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={cities} margin={{ left: -15 }}>
            <XAxis dataKey="label" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
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
