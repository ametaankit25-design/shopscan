// src/components/ListingDetailModal.jsx
import {
  X,
  MapPin,
  Phone,
  ExternalLink,
  Pencil,
  Trash2,
  Star,
  Database,
  Calendar,
} from 'lucide-react';
import { getListingRating } from '../utils/categoryImages';

export default function ListingDetailModal({ listing, onClose, onEdit, onDelete }) {
  if (!listing) return null;

  const rating = getListingRating(listing.id);
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    `${listing.business_name}, ${listing.address || listing.city}`
  )}`;

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal detail-modal">
        {/* Clean Header without image */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="detail-badge-cat">{listing.category || 'General'}</span>
            <span className="detail-badge-rating">
              <Star size={13} fill="#c9a227" color="#c9a227" /> {rating}
            </span>
          </div>
          <button className="btn-close-modal" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="detail-modal-body">
          <div className="detail-title-row">
            <div>
              <h2 className="detail-title">{listing.business_name}</h2>
              <div className="detail-city-pill">
                <MapPin size={13} /> {listing.city}
              </div>
            </div>
          </div>

          <div className="detail-info-grid">
            <div className="detail-info-item" style={{ gridColumn: '1 / -1' }}>
              <MapPin size={16} className="detail-info-icon" />
              <div>
                <div className="detail-info-label">Address</div>
                <div className="detail-info-value">{listing.address || 'Address not provided'}</div>
                <a
                  href={mapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="detail-maps-link"
                >
                  View on Google Maps <ExternalLink size={12} />
                </a>
              </div>
            </div>

            <div className="detail-info-item">
              <Phone size={16} className="detail-info-icon" />
              <div>
                <div className="detail-info-label">Phone</div>
                {listing.phone ? (
                  <a
                    href={`tel:${listing.phone.replace(/[^+\d]/g, '')}`}
                    className="detail-info-value detail-phone-link"
                    title="Call this business"
                  >
                    {listing.phone}
                  </a>
                ) : (
                  <div className="detail-info-value">Not provided</div>
                )}
              </div>
            </div>

            <div className="detail-info-item">
              <Database size={16} className="detail-info-icon" />
              <div>
                <div className="detail-info-label">Data Source</div>
                <div className="detail-info-value source-tag">{listing.source || 'Manual Entry'}</div>
              </div>
            </div>

            <div className="detail-info-item">
              <Calendar size={16} className="detail-info-icon" />
              <div>
                <div className="detail-info-label">Listing ID</div>
                <div className="detail-info-value">#{listing.id}</div>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="detail-modal-actions">
            <div className="detail-meta-left">
              <span>Category: {listing.category}</span>
            </div>

            <div className="detail-btn-group">
              <button
                className="btn btn-secondary detail-btn"
                onClick={() => {
                  onClose();
                  onEdit(listing);
                }}
              >
                <Pencil size={15} /> Edit Listing
              </button>
              <button
                className="btn btn-danger detail-btn"
                onClick={() => {
                  onClose();
                  onDelete(listing);
                }}
              >
                <Trash2 size={15} /> Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
