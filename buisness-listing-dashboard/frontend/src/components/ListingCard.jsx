// src/components/ListingCard.jsx
import { useState } from 'react';
import {
  Heart,
  Star,
  MapPin,
  Utensils,
  Coffee,
  Building,
  Store,
  Cross,
  GraduationCap,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { getListingRating } from '../utils/categoryImages';

// Icon selector for category tags
function getCategoryIcon(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('restaurant') || cat.includes('food') || cat.includes('pizza') || cat.includes('burger')) {
    return <Utensils size={12} />;
  }
  if (cat.includes('cafe') || cat.includes('coffee') || cat.includes('bakery')) {
    return <Coffee size={12} />;
  }
  if (cat.includes('hospital') || cat.includes('clinic') || cat.includes('pharmacy')) {
    return <Cross size={12} />;
  }
  if (cat.includes('school') || cat.includes('college')) {
    return <GraduationCap size={12} />;
  }
  if (cat.includes('retail') || cat.includes('store') || cat.includes('jewellery') || cat.includes('clothing')) {
    return <Store size={12} />;
  }
  if (cat.includes('hotel') || cat.includes('real estate')) {
    return <Building size={12} />;
  }
  return <Sparkles size={12} />;
}

export default function ListingCard({ listing, onViewDetails }) {
  const [isFavorite, setIsFavorite] = useState(() => {
    try {
      const saved = localStorage.getItem(`fav_${listing.id}`);
      return saved === 'true';
    } catch {
      return false;
    }
  });

  const toggleFavorite = (e) => {
    e.stopPropagation();
    const next = !isFavorite;
    setIsFavorite(next);
    try {
      localStorage.setItem(`fav_${listing.id}`, String(next));
    } catch {
      // ignore
    }
  };

  const rating = getListingRating(listing.id);

  return (
    <div className="vazhi-card vazhi-card-no-img" onClick={() => onViewDetails(listing)}>
      {/* ── Card Body ── */}
      <div className="card-body">
        {/* Category & Top Controls */}
        <div className="card-cat-rating">
          <div className="cat-pill">
            <span className="cat-icon-circle">{getCategoryIcon(listing.category)}</span>
            <span className="cat-name">{listing.category || 'General'}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="rating-pill">
              <Star size={13} className="star-icon" fill="#f59e0b" color="#f59e0b" />
              <span className="rating-text">{rating}</span>
            </div>

            <button
              className={`card-inline-heart-btn ${isFavorite ? 'favorited' : ''}`}
              onClick={toggleFavorite}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
              aria-label="Toggle Favorite"
            >
              <Heart
                size={15}
                fill={isFavorite ? '#e64942' : 'none'}
                color={isFavorite ? '#e64942' : '#94a3b8'}
              />
            </button>
          </div>
        </div>

        {/* Business Title */}
        <h3 className="card-title" title={listing.business_name}>
          {listing.business_name}
        </h3>

        {/* Short description */}
        <p className="card-desc">
          Premier services and verified quality experiences located in {listing.city || 'the prime district'}.
        </p>

        {/* Address Detail */}
        <div className="card-details-list">
          <div className="card-detail-item">
            <MapPin size={14} className="detail-icon" />
            <span className="detail-text" title={listing.address}>
              {listing.address || `${listing.city}, India`}
            </span>
          </div>
        </div>

        {/* ── Card Footer ── */}
        <div className="card-footer card-footer-clean">
          <span className="card-city-tag">{listing.city}</span>
          <button
            className="view-details-link"
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails(listing);
            }}
          >
            <span>View Details</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}
