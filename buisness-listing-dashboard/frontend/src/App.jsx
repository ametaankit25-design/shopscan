// src/App.jsx
import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Listings from './pages/Listings';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import ListingModal from './components/ListingModal';
import { ToastProvider } from './context/ToastContext';

function MainApp() {
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="vazhi-app-layout">
      {/* ── Navbar ── */}
      <Header onOpenAddListing={() => setAddModalOpen(true)} />

      {/* ── Main View Pages ── */}
      <main className="vazhi-main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/listings" replace />} />
          <Route path="/listings" element={<Listings key={refreshKey} />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Navigate to="/listings" replace />} />
        </Routes>
      </main>

      {/* ── Global Add Listing Modal ── */}
      {addModalOpen && (
        <ListingModal
          listing={null}
          onClose={() => setAddModalOpen(false)}
          onSaved={() => {
            setRefreshKey((k) => k + 1);
          }}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <MainApp />
      </ToastProvider>
    </BrowserRouter>
  );
}
