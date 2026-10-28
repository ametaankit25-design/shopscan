// src/pages/Analytics.jsx
import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
  LineChart, Line, CartesianGrid,
} from 'recharts';
import { fetchStatsByCategory, fetchStatsByCity, fetchStatsBySource, fetchStatsOverview } from '../api/client';

const COLORS = [
  '#e64942', '#3b82f6', '#10b981', '#f59e0b',
  '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16',
  '#f97316', '#a855f7',
];

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
      <strong>{payload[0].value?.toLocaleString()}</strong> listings
    </div>
  );
};

export default function Analytics() {
  const [categories, setCategories] = useState([]);
  const [cities, setCities] = useState([]);
  const [sources, setSources] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchStatsByCategory(15),
      fetchStatsByCity(15),
      fetchStatsBySource(),
      fetchStatsOverview(),
    ]).then(([cat, cit, src, ov]) => {
      setCategories(cat);
      setCities(cit);
      setSources(src);
      setOverview(ov);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="vazhi-container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <p style={{ color: '#858d9d' }}>Loading advanced directory analytics...</p>
      </div>
    );
  }

  return (
    <div className="vazhi-dashboard-page vazhi-container">
      <div style={{ marginBottom: 32 }}>
        <h1 className="dashboard-hero-title">Directory Analytics</h1>
        <p className="dashboard-hero-subtitle">
          In-depth ranking by category volume, metropolitan concentration, and ingestion feeds.
        </p>
      </div>

      {/* Category – Horizontal Bar */}
      <div className="chart-card-vazhi" style={{ marginBottom: 28 }}>
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
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {categories.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="charts-row-2">
        {/* City Distribution */}
        <div className="chart-card-vazhi">
          <div className="chart-header-row">
            <div>
              <h3 className="chart-title">Destination Coverage</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Top 15 cities with highest directory count</p>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={cities} margin={{ left: -15, bottom: 25 }}>
              <XAxis
                dataKey="label"
                tick={{ fill: '#64748b', fontSize: 10 }}
                tickLine={false}
                axisLine={false}
                interval={0}
                angle={-30}
                textAnchor="end"
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip content={<TooltipBox />} />
              <Bar dataKey="count" fill="#e64942" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Source Breakdown */}
        <div className="chart-card-vazhi">
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
                cy="50%"
                outerRadius={85}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {sources.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<TooltipBox />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
