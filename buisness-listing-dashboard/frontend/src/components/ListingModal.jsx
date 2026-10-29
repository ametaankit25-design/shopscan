// src/components/ListingModal.jsx
import { useState } from 'react';
import { X } from 'lucide-react';
import { createListing, updateListing } from '../api/client';
import { useToast } from '../context/ToastContext';

const EMPTY = {
  business_name: '',
  category: '',
  city: '',
  address: '',
  phone: '',
  source: 'manual_entry',
};

const CATEGORIES = [
  'Restaurant', 'Cafe', 'Hotel', 'Retail Store', 'Grocery',
  'Pharmacy', 'Hospital', 'Clinic', 'School', 'College',
  'Bank', 'ATM', 'Salon', 'Spa', 'Gym', 'Bakery',
  'Electronics', 'Clothing', 'Furniture', 'Real Estate',
  'Automobile', 'Petrol Station', 'Hardware', 'Bookstore', 'Jewellery',
];

export default function ListingModal({ listing, onClose, onSaved }) {
  // The modal is mounted fresh each time it opens, so initial state can come straight from props.
  const [form, setForm] = useState(() => (listing ? {
    business_name: listing.business_name ?? '',
    category: listing.category ?? '',
    city: listing.city ?? '',
    address: listing.address ?? '',
    phone: listing.phone ?? '',
    source: listing.source ?? 'manual_entry',
  } : EMPTY));
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  const handle = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v === '' ? null : v])
      );
      if (listing) {
        await updateListing(listing.id, payload);
        toast('Listing updated successfully', 'success');
      } else {
        await createListing(payload);
        toast('Listing created successfully', 'success');
      }
      onSaved();
      onClose();
    } catch (err) {
      toast(err?.response?.data?.detail ?? 'Something went wrong', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2 className="modal-title">{listing ? 'Edit Business Listing' : 'Add New Listing'}</h2>
          <button className="btn-close-modal" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={submit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">Business Name *</label>
              <input
                name="business_name"
                className="form-input"
                value={form.business_name}
                onChange={handle}
                required
                placeholder="e.g. Steak and Chop House"
              />
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label className="form-label">Category *</label>
                <select
                  name="category"
                  className="form-select"
                  value={form.category}
                  onChange={handle}
                  required
                >
                  <option value="">Select Category</option>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">City *</label>
                <input
                  name="city"
                  className="form-input"
                  value={form.city}
                  onChange={handle}
                  required
                  placeholder="e.g. Mumbai, Dubai, London"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Address</label>
              <textarea
                name="address"
                className="form-textarea"
                value={form.address}
                onChange={handle}
                rows={3}
                placeholder="Full street address and building number"
              />
            </div>

            <div className="form-row-2">
              <div className="form-group">
                <label className="form-label">Phone Number</label>
                <input
                  name="phone"
                  className="form-input"
                  value={form.phone}
                  onChange={handle}
                  placeholder="+91-9876543210"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Data Source</label>
                <select
                  name="source"
                  className="form-select"
                  value={form.source}
                  onChange={handle}
                >
                  <option value="manual_entry">manual_entry</option>
                  <option value="web_scraper">web_scraper</option>
                  <option value="google_places">google_places</option>
                  <option value="justdial_import">justdial_import</option>
                  <option value="csv_upload">csv_upload</option>
                </select>
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-vazhi-primary" disabled={saving}>
              {saving ? 'Saving…' : listing ? 'Save Changes' : 'Create Listing'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
