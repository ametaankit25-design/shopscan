// src/components/ConfirmModal.jsx
import { AlertTriangle, X } from 'lucide-react';

export default function ConfirmModal({
  title = 'Confirm Delete',
  message,
  confirmLabel = 'Delete',
  onConfirm,
  onCancel,
  onClose,
  loading = false,
}) {
  const handleDismiss = onCancel || onClose;

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && handleDismiss?.()}>
      <div className="modal" style={{ maxWidth: 420 }}>
        <div className="modal-header" style={{ borderBottom: 'none', paddingBottom: 0 }}>
          <div />
          <button className="btn-close-modal" onClick={handleDismiss}>
            <X size={18} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', textAlign: 'center', padding: '0 1rem 1rem' }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              background: '#fef2f2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <AlertTriangle size={28} color="#e64942" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1e2229', marginBottom: '0.5rem' }}>
              {title}
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: 1.5 }}>{message}</p>
          </div>
        </div>

        <div className="modal-footer" style={{ justifyContent: 'center', gap: '0.75rem', background: '#fafbfc' }}>
          <button className="btn btn-secondary" onClick={handleDismiss} disabled={loading}>
            Cancel
          </button>
          <button className="btn btn-danger" onClick={onConfirm} disabled={loading}>
            {loading ? 'Deleting…' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
