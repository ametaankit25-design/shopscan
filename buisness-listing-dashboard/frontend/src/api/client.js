// src/api/client.js
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

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

export default client;
