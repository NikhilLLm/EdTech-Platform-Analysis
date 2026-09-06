import React from 'react';
import { 
  BarChart3, 
  Layers, 
  GitCompare, 
  Calendar, 
  TrendingUp, 
  Activity, 
  Sparkles 
} from 'lucide-react';

export default function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'executive', label: 'Executive Summary', icon: Sparkles },
    { id: 'funnel', label: 'Funnel & Drop-Offs', icon: Layers },
    { id: 'cohorts', label: 'Cohort Retention', icon: Calendar },
    { id: 'ab_test', label: 'A/B Experiment', icon: GitCompare },
    { id: 'churn_pay', label: 'Churn & Monetization', icon: TrendingUp }
  ];

  return (
    <header className="header-container">
      <div className="header-inner">
        <div className="brand-section">
          <div className="brand-icon">
            <Activity size={22} />
          </div>
          <div>
            <h1 className="brand-title">
              EdTech Growth Analytics
              <span className="badge-live">
                <span className="badge-dot"></span>
                DuckDB Modeled
              </span>
            </h1>
            <p className="brand-subtitle">100K Users • 149.3K Enrollments • 3.5M Behavioral Events</p>
          </div>
        </div>

        <nav className="nav-tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                className={`nav-tab ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
