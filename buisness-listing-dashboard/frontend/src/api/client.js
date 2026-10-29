// src/api/client.js
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

/** Human-readable message for a failed API call (network down vs. HTTP error). */
export const describeApiError = (err) => {
  if (!err?.response) {
    return `Cannot reach the API at ${BASE_URL}. Make sure the FastAPI server is running.`;
  }
  const detail = err.response.data?.detail;
  return typeof detail === 'string' ? detail : `The API returned an error (HTTP ${err.response.status}).`;
};

// ── Listings ──────────────────────────────────────────────────────────────────

export const fetchListings = (params) =>
  client.get('/listings', { params }).then((r) => r.data);

export const fetchListing = (id) =>
  client.get(`/listings/${id}`).then((r) => r.data);

export const createListing = (data) =>
  client.post('/listings', data).then((r) => r.data);

export const updateListing = (id, data) =>
  client.patch(`/listings/${id}`, data).then((r) => r.data);

export const deleteListing = (id) =>
  client.delete(`/listings/${id}`);

// ── Stats ─────────────────────────────────────────────────────────────────────

export const fetchStatsOverview = () =>
  client.get('/stats/overview').then((r) => r.data);

export const fetchStatsByCategory = (limit = 10) =>
  client.get('/stats/category', { params: { limit } }).then((r) => r.data);

export const fetchStatsByCity = (limit = 10) =>
  client.get('/stats/city', { params: { limit } }).then((r) => r.data);

export const fetchStatsBySource = () =>
  client.get('/stats/source').then((r) => r.data);

export const fetchStatsTimeline = (days = 30) =>
  client.get('/stats/timeline', { params: { days } }).then((r) => r.data);

export const fetchStatsCityCategory = (cities = 8, categories = 6) =>
  client.get('/stats/city-category', { params: { cities, categories } }).then((r) => r.data);

export default client;
