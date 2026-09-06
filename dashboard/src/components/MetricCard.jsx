import React from 'react';

export default function MetricCard({ title, value, subtitle, badgeText, badgeType = 'success', icon: Icon }) {
  return (
    <div className="kpi-card">
      <div className="kpi-top">
        <span className="kpi-label">{title}</span>
        {Icon && (
          <div className="kpi-icon-wrap">
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="kpi-val">{value}</div>
      <div className="kpi-footer">
        {badgeText && (
          <span className={badgeType === 'danger' ? 'kpi-pill-danger' : 'kpi-pill-success'}>
            {badgeText}
          </span>
        )}
        <span>{subtitle}</span>
      </div>
    </div>
  );
}
