// src/pages/Listings.jsx
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Search,
  MapPin,
  Layers,
  ChevronRight,
  ChevronLeft,
  RotateCcw,
  Plus,
} from 'lucide-react';
import { fetchListings, deleteListing } from '../api/client';
import { useToast } from '../context/ToastContext';
import ListingCard from '../components/ListingCard';
import ListingDetailModal from '../components/ListingDetailModal';
import ListingModal from '../components/ListingModal';
import ConfirmModal from '../components/ConfirmModal';

const CATEGORIES = [
  'Restaurant', 'Cafe', 'Hotel', 'Retail Store', 'Grocery',
  'Pharmacy', 'Hospital', 'Clinic', 'School', 'College',
  'Bank', 'ATM', 'Salon', 'Spa', 'Gym', 'Bakery',
  'Electronics', 'Clothing', 'Furniture', 'Real Estate',
  'Automobile', 'Petrol Station', 'Hardware', 'Bookstore', 'Jewellery',
];

const CITIES = [
  'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad',
  'Chennai', 'Kolkata', 'Pune', 'Jaipur', 'Lucknow',
  'Surat', 'Kanpur', 'Nagpur', 'Indore', 'Thane',
  'Bhopal', 'Visakhapatnam', 'Pimpri', 'Patna', 'Vadodara',
];

const PAGE_SIZE = 16; // 4 columns x 4 rows matches the screenshot grid

function useDebouncedValue(value, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function Listings({ onAddListingTrigger }) {
  const [data, setData] = useState({ total: 0, items: [] });
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filterCity, setFilterCity] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [loading, setLoading] = useState(true);

  // Modals state
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [modalListing, setModalListing] = useState(undefined); // undefined = closed, null = new, obj = edit
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const toast = useToast();
  const debouncedSearch = useDebouncedValue(search);
  const abortRef = useRef(null);

  const load = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setLoading(true);

    fetchListings({
      page,
      page_size: PAGE_SIZE,
      search: debouncedSearch || undefined,
      category: filterCategory || undefined,
      city: filterCity || undefined,
    })
      .then(setData)
      .catch((e) => {
        if (e?.code !== 'ERR_CANCELED') toast('Failed to load listings', 'error');
      })
      .finally(() => setLoading(false));
  }, [page, debouncedSearch, filterCategory, filterCity]);

  useEffect(() => {
    load();
  }, [load]);

  // Reset page to 1 on any filter change
  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, filterCategory, filterCity]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteListing(deleteTarget.id);
      toast(`"${deleteTarget.business_name}" deleted`, 'success');
      setDeleteTarget(null);
      setSelectedDetail(null);
      load();
    } catch {
      toast('Failed to delete listing', 'error');
    } finally {
      setDeleting(false);
    }
  };

  const handleResetFilters = () => {
    setSearch('');
    setFilterCity('');
    setFilterCategory('');
  };

  const totalPages = Math.max(1, Math.ceil(data.total / PAGE_SIZE));
  const start = Math.min((page - 1) * PAGE_SIZE + 1, data.total);
  const end = Math.min(page * PAGE_SIZE, data.total);

  // Generate pagination items
  const getPaginationItems = () => {
    const items = [];
    const maxVisible = 5;
    let startPage = Math.max(1, page - 2);
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage + 1 < maxVisible) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let p = startPage; p <= endPage; p++) {
      items.push(p);
    }
    return items;
  };

  const hasActiveFilters = Boolean(search || filterCity || filterCategory);

  return (
    <div className="vazhi-listings-page">
      {/* ── 1. Hero Page Title & Breadcrumbs ── */}
      <section className="vazhi-hero">
        <div className="vazhi-container hero-center">
          <h1 className="hero-page-title">Listing</h1>
          <div className="hero-breadcrumbs">
            <span>Directory</span>
            <span className="breadcrumb-dot">•</span>
            <span className="current">Listings</span>
          </div>

          {/* ── Floating 3-Segment Search Bar ── */}
          <div className="hero-search-card">
            {/* Segment 1: Looking For */}
            <div className="search-field-segment">
              <label className="segment-label">1. Looking For</label>
              <div className="segment-input-wrap">
                <input
                  type="text"
                  placeholder="Seeking Places..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="segment-input"
                />
              </div>
            </div>

            <div className="segment-divider" />

            {/* Segment 2: Destination */}
            <div className="search-field-segment">
              <label className="segment-label">2. Destination</label>
              <div className="segment-input-wrap">
                <input
                  type="text"
                  list="city-options"
                  placeholder="Search Locations..."
                  value={filterCity}
                  onChange={(e) => setFilterCity(e.target.value)}
                  className="segment-input"
                />
                <MapPin size={15} className="segment-icon-right" />
                <datalist id="city-options">
                  {CITIES.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </div>
            </div>

            <div className="segment-divider" />

            {/* Segment 3: Highlights / Category */}
            <div className="search-field-segment">
              <label className="segment-label">3. Highlights</label>
              <div className="segment-input-wrap select-wrap">
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="segment-select"
                >
                  <option value="">Categories</option>
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Red Search Button */}
            <button
              className="hero-search-btn"
              onClick={() => load()}
              title="Search Listings"
              aria-label="Search"
            >
              <Search size={22} strokeWidth={2.5} />
            </button>
          </div>
        </div>
      </section>

      {/* ── 2. Results Header & Controls ── */}
      <section className="vazhi-container listings-content-wrap">
        <div className="listings-meta-row">
          <div className="results-count-text">
            {loading ? (
              <span>Searching listings...</span>
            ) : data.total > 0 ? (
              <span>
                Showing <strong>{start}–{end}</strong> of <strong>{data.total}</strong> Results
              </span>
            ) : (
              <span>No results found</span>
            )}
          </div>

          <div className="meta-actions-right">
            {hasActiveFilters && (
              <button className="reset-filter-btn" onClick={handleResetFilters}>
                <RotateCcw size={13} /> Reset Filters
              </button>
            )}

            <button
              className="add-quick-btn"
              onClick={() => setModalListing(null)}
              id="page-add-listing-btn"
            >
              <Plus size={15} /> Add Business
            </button>
          </div>
        </div>

        {/* ── 3. Listings 4-Column Grid ── */}
        {loading ? (
          <div className="listings-grid">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="card-skeleton">
                <div className="skeleton-img" />
                <div className="skeleton-content">
                  <div className="skeleton-line w-40" />
                  <div className="skeleton-line w-80" />
                  <div className="skeleton-line w-60" />
                  <div className="skeleton-line w-50" />
                </div>
              </div>
            ))}
          </div>
        ) : data.items.length === 0 ? (
          <div className="empty-state-box">
            <Layers size={48} className="empty-icon" />
            <h3 className="empty-title">No Listings Match Your Search</h3>
            <p className="empty-sub">
              Try adjusting your keyword, choosing another destination, or clearing active filters.
            </p>
            <button className="btn-vazhi-primary" onClick={handleResetFilters}>
              Clear All Filters
            </button>
          </div>
        ) : (
          <div className="listings-grid">
            {data.items.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onViewDetails={setSelectedDetail}
                onEdit={(item) => setModalListing(item)}
                onDelete={(item) => setDeleteTarget(item)}
              />
            ))}
          </div>
        )}

        {/* ── 4. Circular Red Numbered Pagination ── */}
        {totalPages > 1 && (
          <div className="vazhi-pagination">
            <button
              className="page-nav-btn prev"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>

            {getPaginationItems().map((p) => (
              <button
                key={p}
                className={`page-num-btn ${page === p ? 'active' : ''}`}
                onClick={() => setPage(p)}
              >
                {p}
              </button>
            ))}

            {page < totalPages && (
              <button
                className="page-nav-btn next"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                aria-label="Next page"
              >
                <ChevronRight size={16} />
              </button>
            )}
          </div>
        )}
      </section>

      {/* ── Modals ── */}
      {selectedDetail && (
        <ListingDetailModal
          listing={selectedDetail}
          onClose={() => setSelectedDetail(null)}
          onEdit={(item) => setModalListing(item)}
          onDelete={(item) => setDeleteTarget(item)}
        />
      )}

      {modalListing !== undefined && (
        <ListingModal
          listing={modalListing}
          onClose={() => setModalListing(undefined)}
          onSaved={() => {
            load();
            if (selectedDetail && modalListing && selectedDetail.id === modalListing.id) {
              setSelectedDetail(null);
            }
          }}
        />
      )}

      {deleteTarget && (
        <ConfirmModal
          title="Delete Business Listing"
          message={`Are you sure you want to permanently delete "${deleteTarget.business_name}"? This action cannot be undone.`}
          confirmLabel="Delete Listing"
          loading={deleting}
          onConfirm={handleDelete}
          onClose={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
