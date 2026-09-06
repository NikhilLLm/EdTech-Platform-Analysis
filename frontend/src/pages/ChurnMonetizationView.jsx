import React from 'react';
import { TrendingUp, ShieldAlert, DollarSign, Activity, AlertCircle, Award } from 'lucide-react';

export default function ChurnMonetizationView({ data }) {
  const churn = data.churn_risk || {};
  const paymentDrivers = data.payment_drivers || {};
  const categorySummary = data.category_summary || [];
  const segments = churn.segment_distribution || [];
  const churnOdds = churn.odds_ratios || [];
  const payOdds = paymentDrivers.odds_ratios || [];

  const testAuc = churn.test_roc_auc || 0.7831;
  const payAuc = paymentDrivers.model_auc || 0.5675;

  return (
    <div>
      {/* Analysis Charts from Python Pipeline */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">Churn Risk Distribution & Model Performance</h3>
            <p className="card-subtitle">Logistic Regression on 86,926 enrolled users — Holdout AUC: 0.7831</p>
          </div>
        </div>
        <img
          src="/05_churn_risk_distribution.png"
          alt="Churn Risk Distribution"
          style={{ width: '100%', borderRadius: '8px', marginTop: '12px', display: 'block' }}
        />
      </div>

      <div className="card" style={{ marginBottom: '28px' }}>

        <div className="card-header">
          <div>
            <h2 className="card-title">
              <ShieldAlert size={20} color="var(--accent-rose)" />
              Supervised Churn Risk Modeling (Q4)
            </h2>
            <p className="card-subtitle">
              Leakage-free Logistic Regression trained on 80% split and validated on 20% holdout (N = 86,926 Enrolled Users)
            </p>
          </div>
          <div className="badge-live" style={{ background: 'rgba(56, 189, 248, 0.15)', color: 'var(--accent-blue)', borderColor: 'rgba(56, 189, 248, 0.3)' }}>
            Holdout Test ROC-AUC: <strong>{testAuc}</strong>
          </div>
        </div>

        <div className="grid-2">
          {/* Churn Odds Ratios Table & Forest View */}
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '12px', color: 'var(--text-muted)' }}>
              Feature Log-Odds Coefficients & Odds Ratios
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {churnOdds.map((feat) => {
                const coef = feat.Coefficient;
                const orVal = feat.Odds_Ratio;
                const isProtective = coef < 0;

                return (
                  <div key={feat.Feature} style={{ background: 'rgba(255,255,255,0.02)', padding: '10px 14px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.84rem' }}>{feat.Feature}</span>
                      <span style={{ 
                        fontFamily: 'var(--font-mono)', 
                        fontSize: '0.82rem', 
                        fontWeight: 700,
                        color: isProtective ? 'var(--accent-emerald)' : 'var(--accent-rose)'
                      }}>
                        OR = {orVal.toFixed(4)}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      {feat.Feature === 'activated_int' && 'Completing Lesson 1 within 2 days reduces churn odds by 99.9% (OR: 0.0006).'}
                      {feat.Feature === 'quiz_pass_rate' && 'Higher quiz pass rate heavily protects against course abandonment.'}
                      {feat.Feature === 'total_enrolled_courses' && 'Learners enrolled in multiple courses exhibit 50% lower churn odds.'}
                      {feat.Feature.startsWith('signup_channel') && 'Acquisition channel shows near-neutral impact on learner persistence.'}
                      {feat.Feature === 'age_clean' && 'Age demonstrates minimal correlation with course completion.'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Churn Segmentation Table */}
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '12px', color: 'var(--text-muted)' }}>
              Platform User Churn Risk Distribution (mart_churn_risk)
            </h4>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Risk Segment</th>
                    <th>User Count</th>
                    <th>Cohort %</th>
                  </tr>
                </thead>
                <tbody>
                  {segments.map((s) => (
                    <tr key={s.churn_risk_segment}>
                      <td style={{ fontWeight: 600 }}>{s.churn_risk_segment}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{s.user_count.toLocaleString()}</td>
                      <td>
                        <span className="badge-live" style={{ 
                          background: s.churn_risk_segment === 'Completed All' ? 'rgba(16, 185, 129, 0.15)' : 
                                      s.churn_risk_segment === 'High Churn Risk' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                          color: s.churn_risk_segment === 'Completed All' ? '#34d399' : 
                                 s.churn_risk_segment === 'High Churn Risk' ? '#fb7185' : 'var(--accent-blue)',
                          borderColor: 'transparent'
                        }}>
                          {s.pct}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="callout-box callout-success" style={{ marginTop: '20px' }}>
              <strong>Zero Data Leakage Confirmed:</strong> Both <code>completion_ratio</code> and <code>days_since_last_activity</code> were strictly excluded from model predictors. The resulting <strong>AUC = 0.7831</strong> represents genuine, early behavioral discrimination.
            </div>
          </div>
        </div>
      </div>

      {/* Payment Conversion Chart from Python Pipeline */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">Payment Conversion Drivers</h3>
            <p className="card-subtitle">Logistic Regression on 69,597 completed enrollments — category & quiz signal analysis</p>
          </div>
        </div>
        <img
          src="/04_payment_conversion_drivers.png"
          alt="Payment Conversion Drivers"
          style={{ width: '100%', borderRadius: '8px', marginTop: '12px', display: 'block' }}
        />
      </div>

      {/* 2. PAYMENT CONVERSION DRIVERS SECTION */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <DollarSign size={20} color="var(--accent-amber)" />
              Payment Conversion Drivers & Willingness to Pay (Q5)
            </h2>
            <p className="card-subtitle">
              Evaluated across 69,597 completed enrollments (mart_payment_conversion)
            </p>
          </div>
          <div className="badge-live" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
            Overall Certification Rate: <strong>27.5%</strong>
          </div>
        </div>

        <div className="grid-2">
          {/* Category Conversion Rates */}
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '12px', color: 'var(--text-muted)' }}>
              Certification Conversion Rate by Course Category
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {categorySummary.map((cat) => {
                const rate = cat.conversion_pct;
                const isTech = ['cloud_devops', 'programming', 'data_analytics'].includes(cat.course_category);

                return (
                  <div key={cat.course_category} style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.84rem' }}>
                      <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                        {cat.course_category.replace('_', ' ')}
                      </span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: isTech ? 'var(--accent-blue)' : 'var(--accent-amber)' }}>
                        {cat.total_paid.toLocaleString()} / {cat.total_completed.toLocaleString()} ({rate}%)
                      </span>
                    </div>
                    <div style={{ height: '18px', background: 'rgba(255,255,255,0.04)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div 
                        style={{ 
                          height: '100%', 
                          width: `${(rate / 40) * 100}%`, 
                          background: isTech ? 'linear-gradient(90deg, #2563eb, #38bdf8)' : 'linear-gradient(90deg, #d97706, #fbbf24)',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Executive Monetization Summary */}
          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '12px', color: 'var(--text-muted)' }}>
              Key Pricing & Monetization Insights
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', borderLeft: '3px solid var(--accent-blue)' }}>
                <strong style={{ fontSize: '0.84rem' }}>1. Technical Disciplines Drive Higher Conversion</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                  Cloud DevOps (33.1%) and Programming (30.5%) convert at significantly higher rates than Design (20.1%), yielding Odds Ratios of <strong>1.97</strong> and <strong>1.75</strong> respectively vs. baseline design. Career-advancement potential justifies certification fees.
                </p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', borderLeft: '3px solid var(--accent-emerald)' }}>
                <strong style={{ fontSize: '0.84rem' }}>2. Academic Engagement Depth Matters</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                  Learners in the top quartile of quiz pass rates convert at <strong>30.0%</strong> compared to <strong>25.3%</strong> in the bottom quartile (Logistic Regression OR = <strong>3.30</strong>, p &lt; 10⁻²⁵).
                </p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', borderLeft: '3px solid var(--accent-amber)' }}>
                <strong style={{ fontSize: '0.84rem' }}>3. Channel Neutrality</strong>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                  Signup channel coefficients were statistically indistinguishable from zero (all p &gt; 0.70). Monetization strategy should segment by course topic rather than acquisition channel.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
