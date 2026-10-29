// src/components/ErrorState.jsx
import { AlertTriangle, RotateCcw } from 'lucide-react';

export default function ErrorState({ title = 'Could not load data', message, onRetry }) {
  return (
    <div className="vazhi-container state-panel" role="alert">
      <AlertTriangle size={32} className="state-panel-icon" />
      <h2 className="state-panel-title">{title}</h2>
      {message && <p className="state-panel-message">{message}</p>}
      {onRetry && (
        <button type="button" className="btn-vazhi-primary state-panel-btn" onClick={onRetry}>
          <RotateCcw size={16} /> Retry
        </button>
      )}
    </div>
  );
}
