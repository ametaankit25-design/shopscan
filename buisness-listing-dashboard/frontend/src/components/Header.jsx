// src/components/Header.jsx
import { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { Plus, Menu, X, Sparkles } from 'lucide-react';

export default function Header({ onOpenAddListing }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isListingsActive = location.pathname === '/' || location.pathname === '/listings';

  return (
    <header className="vazhi-header">
      {/* ── Main Navigation ────────────────────────────────────────── */}
      <div className="vazhi-navbar">
        <div className="vazhi-container vazhi-navbar-content">
          {/* Logo: Shop Skin */}
          <Link to="/listings" className="vazhi-logo">
            <div className="logo-badge">
              <Sparkles size={18} />
            </div>
            <span className="logo-text">Shop Skin</span>
          </Link>

          {/* Desktop Nav Links */}
          <nav className="vazhi-nav-links">
            <NavLink
              to="/listings"
              className={() => (isListingsActive ? 'nav-item active' : 'nav-item')}
            >
              Listings
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/analytics"
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              Analytics
            </NavLink>
          </nav>

          {/* Action Buttons: Add Listing */}
          <div className="vazhi-actions">
            <button
              className="btn-add-listing"
              onClick={onOpenAddListing}
              id="header-add-listing-btn"
            >
              <Plus size={16} strokeWidth={2.5} />
              <span>Add Listing</span>
            </button>

            {/* Mobile Hamburger */}
            <button
              className="mobile-toggle-btn"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle Navigation"
            >
              {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="mobile-menu">
            <NavLink
              to="/listings"
              onClick={() => setMobileMenuOpen(false)}
              className="mobile-nav-item"
            >
              Listings
            </NavLink>
            <NavLink
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="mobile-nav-item"
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/analytics"
              onClick={() => setMobileMenuOpen(false)}
              className="mobile-nav-item"
            >
              Analytics
            </NavLink>
            <button
              className="btn-add-listing mobile-add"
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenAddListing();
              }}
            >
              <Plus size={16} /> Add Listing
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
