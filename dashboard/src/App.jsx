import React, { useState } from 'react';
import Navigation from './components/Navigation';
import ExecutiveOverview from './pages/ExecutiveOverview';
import FunnelView from './pages/FunnelView';
import CohortView from './pages/CohortView';
import ExperimentView from './pages/ExperimentView';
import ChurnMonetizationView from './pages/ChurnMonetizationView';
import metricsData from './data/metrics.json';

export default function App() {
  const [activeTab, setActiveTab] = useState('executive');

  return (
    <div className="app-container">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {activeTab === 'executive' && (
          <ExecutiveOverview data={metricsData} setActiveTab={setActiveTab} />
        )}
        {activeTab === 'funnel' && (
          <FunnelView data={metricsData} />
        )}
        {activeTab === 'cohorts' && (
          <CohortView data={metricsData} />
        )}
        {activeTab === 'ab_test' && (
          <ExperimentView data={metricsData} />
        )}
        {activeTab === 'churn_pay' && (
          <ChurnMonetizationView data={metricsData} />
        )}
      </main>

      <footer className="footer">
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <strong>EdTech Platform Growth Analytics</strong> • Full-Stack Analytics Engineering Portfolio Project
          </div>
          <div style={{ display: 'flex', gap: '16px', color: 'var(--text-dim)' }}>
            <span>DuckDB SQL</span>
            <span>•</span>
            <span>Python statsmodels & scikit-learn</span>
            <span>•</span>
            <span>Vercel Deployable</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
