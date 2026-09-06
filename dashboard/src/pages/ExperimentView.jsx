import React, { useState } from 'react';
import { GitCompare, CheckCircle2, XCircle, Info, Sparkles } from 'lucide-react';

export default function ExperimentView({ data }) {
  const [viewMode, setViewMode] = useState('step_conditional');
  const abData = data.ab_test || {};
  const stepStages = abData.step_conditional || [];
  const cumStages = abData.cumulative || [];

  const currentStages = viewMode === 'step_conditional' ? stepStages : cumStages;

  return (
    <div>
      {/* Header & Toggle */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '14px', alignItems: 'center' }}>
          <div>
            <h2 className="card-title">
              <GitCompare size={20} color="var(--accent-blue)" />
              Onboarding Experiment A/B Test Evaluation (Q3)
            </h2>
            <p className="card-subtitle">
              Randomized Controlled Trial across 100,000 users (50,102 Treatment vs. 49,898 Control)
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Evaluation Perspective:</span>
            <div className="btn-group">
              <button
                className={`btn-toggle ${viewMode === 'step_conditional' ? 'active' : ''}`}
                onClick={() => setViewMode('step_conditional')}
              >
                Step-Conditional (Recommended)
              </button>
              <button
                className={`btn-toggle ${viewMode === 'cumulative' ? 'active' : ''}`}
                onClick={() => setViewMode('cumulative')}
              >
                Cumulative Top-of-Funnel
              </button>
            </div>
          </div>
        </div>

        {viewMode === 'step_conditional' ? (
          <div className="callout-box callout-success">
            <strong>Why Step-Conditional Evaluation is Critical:</strong> Evaluating P(Stage_k | Stage_&#x200b;(k-1)) isolates exactly where the intervention acts. Notice that treatment produces a massive, statistically significant <strong>+6.98% lift at Activation (p &lt; 0.0001)</strong>, while downstream stages naturally decay (+1.10% completion, +4.22% payment), proving the onboarding tutorial drove genuine activation rather than compounding artifacts.
          </div>
        ) : (
          <div className="callout-box">
            <strong>Cumulative Perspective Note:</strong> Top-of-funnel rates (N&#x2081; / N&#x2080;) measure end-to-end business volume. Because treatment activated more users upstream, all downstream headcounts naturally swell (+6.8% activated, +8.0% completed, +12.6% paid).
          </div>
        )}
      </div>

      {/* Analysis Chart from Python Pipeline */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">A/B Test — 4-Stage Lift Analysis</h3>
            <p className="card-subtitle">Two-proportion Z-tests across 100,000 users (Control vs. Treatment)</p>
          </div>
        </div>
        <img
          src="/03_ab_test_4stage_lift.png"
          alt="A/B Test 4-Stage Lift Chart"
          style={{ width: '100%', borderRadius: '8px', marginTop: '12px', display: 'block' }}
        />
      </div>


      <div className="grid-2">
        {/* Visual Stage Bars */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Conversion Rate Comparison</h3>
              <p className="card-subtitle">Control vs. Treatment across 4 funnel stages</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '10px' }}>
            {currentStages.map((stg) => {
              const cVal = stg.Control_Rate_Pct;
              const tVal = stg.Treatment_Rate_Pct;
              const lift = stg.Relative_Lift_Pct;
              const isSig = stg.Significant_p05;

              return (
                <div key={stg.Stage} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: 600 }}>
                    <span>{stg.Stage}</span>
                    <span style={{ 
                      color: isSig && lift > 0 ? 'var(--accent-emerald)' : (isSig && lift < 0 ? 'var(--accent-rose)' : 'var(--text-muted)'),
                      fontFamily: 'var(--font-mono)'
                    }}>
                      {lift >= 0 ? `+${lift.toFixed(2)}%` : `${lift.toFixed(2)}%`} {isSig ? '★' : '(n.s.)'}
                    </span>
                  </div>

                  {/* Control Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ width: '70px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>Control:</span>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '18px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${cVal}%`, height: '100%', background: '#64748b', borderRadius: '3px' }} />
                    </div>
                    <span style={{ width: '55px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {cVal.toFixed(1)}%
                    </span>
                  </div>

                  {/* Treatment Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ width: '70px', fontSize: '0.75rem', color: 'var(--accent-blue)', fontWeight: 600 }}>Treatment:</span>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '18px', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${tVal}%`, height: '100%', background: 'linear-gradient(90deg, #2563eb, #38bdf8)', borderRadius: '3px' }} />
                    </div>
                    <span style={{ width: '55px', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-blue)', fontWeight: 600 }}>
                      {tVal.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Statistical Z-Test Table */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Two-Proportion Z-Test Details</h3>
              <p className="card-subtitle">Formal hypothesis tests (α = 0.05, 95% CIs)</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Diff (% pts)</th>
                  <th>Z-Score</th>
                  <th>P-Value</th>
                  <th>95% CI</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {currentStages.map((stg) => {
                  const p = stg.P_Value;
                  const star = p < 0.001 ? '***' : (p < 0.01 ? '**' : (p < 0.05 ? '*' : 'n.s.'));
                  return (
                    <tr key={stg.Stage}>
                      <td style={{ fontWeight: 600, fontSize: '0.82rem' }}>{stg.Stage}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', color: stg.Diff_Pct_Points > 0 ? 'var(--accent-emerald)' : 'inherit' }}>
                        {stg.Diff_Pct_Points > 0 ? `+${stg.Diff_Pct_Points.toFixed(2)}` : stg.Diff_Pct_Points.toFixed(2)}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{stg.Z_Score.toFixed(2)}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{p < 0.0001 ? '< 0.0001' : p.toFixed(4)}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        [{stg.CI_95_Lower}%, {stg.CI_95_Upper}%]
                      </td>
                      <td>
                        {stg.Significant_p05 ? (
                          <span className="badge-live" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                            Significant {star}
                          </span>
                        ) : (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', padding: '2px 6px' }}>
                            Flat (n.s.)
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="callout-box" style={{ marginTop: '20px' }}>
            <strong>Recommendation for Leadership:</strong> The onboarding experience delivered a confirmed <strong>+5.8 percentage-point lift</strong> directly in Lesson 1 activation (z = 24.61). Recommend rolling out to 100% of incoming users immediately.
          </div>
        </div>
      </div>
    </div>
  );
}
