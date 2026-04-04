import streamlit as st

st.set_page_config(
    page_title="Diabetes Analytics Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# most of the styling is here — took a while to get the hero section right
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

.stApp {
    background: #0a1628;
}

.hero-section {
    background: linear-gradient(135deg, #0d2137 0%, #0a1628 50%, #0d1f35 100%);
    border: 1px solid rgba(0, 200, 180, 0.15);
    border-radius: 20px;
    padding: 60px 50px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}

/* decorative blobs behind the hero text */
.hero-section::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,200,180,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-section::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -60px;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(52,152,219,0.07) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-badge {
    display: inline-block;
    background: rgba(0, 200, 180, 0.1);
    border: 1px solid rgba(0, 200, 180, 0.3);
    color: #00c8b4;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    padding: 6px 14px;
    border-radius: 20px;
    margin-bottom: 20px;
    text-transform: uppercase;
}

.hero-title {
    font-size: 52px;
    font-weight: 700;
    color: #f0f4f8;
    line-height: 1.15;
    margin: 0 0 16px 0;
    letter-spacing: -1px;
}

.hero-title span {
    color: #00c8b4;
}

.hero-subtitle {
    font-size: 18px;
    font-weight: 300;
    color: #8899aa;
    line-height: 1.7;
    max-width: 560px;
    margin: 0 0 40px 0;
}

.nav-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 28px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.nav-card:hover {
    border-color: rgba(0, 200, 180, 0.3);
    background: rgba(0, 200, 180, 0.05);
    transform: translateY(-2px);
}

.nav-card-icon { font-size: 28px; margin-bottom: 12px; display: block; }
.nav-card-title { font-size: 16px; font-weight: 600; color: #e0eaf4; margin-bottom: 6px; }
.nav-card-desc { font-size: 13px; color: #667788; line-height: 1.5; }
.nav-card-arrow { position: absolute; top: 28px; right: 24px; color: #00c8b4; font-size: 18px; opacity: 0.5; }

.stat-row {
    display: flex;
    gap: 20px;
    margin-top: 40px;
}

.stat-item { text-align: center; flex: 1; }

.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #00c8b4;
    line-height: 1;
}

.stat-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #556677;
    margin-top: 6px;
}

.stat-divider { width: 1px; background: rgba(255,255,255,0.07); flex: 0; min-width: 1px; }

.info-strip {
    background: rgba(52, 152, 219, 0.06);
    border: 1px solid rgba(52, 152, 219, 0.15);
    border-radius: 12px;
    padding: 16px 22px;
    margin-top: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #7aafcf;
    font-size: 13px;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<p style="font-family: Space Mono, monospace; font-size:10px; letter-spacing:2px; '
        'text-transform:uppercase; color:#445566;">Navigation</p>',
        unsafe_allow_html=True
    )
    st.markdown("Use the **Pages** menu above to switch sections.")
    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px; color:#556677; line-height:1.8;">
    <b style="color:#8899aa">Descriptive</b><br>
    County-level prevalence across Kenya's 47 counties.<br><br>
    <b style="color:#8899aa">Risk Prediction</b><br>
    ML-powered individual risk scoring with history tracking.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
    <div class="hero-badge">Kenya Health Analytics</div>
    <div class="hero-title">Diabetes<br>Analytics <span>Dashboard</span></div>
    <div class="hero-subtitle">
        Explore county-level diabetes prevalence across Kenya and assess individual risk
        using a machine learning prediction model.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-card-arrow">→</span>
        <div class="nav-card-title">Descriptive Analysis</div>
        <div class="nav-card-desc">Choropleth maps, prevalence rankings, and distribution charts across all 47 counties.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-card-arrow">→</span>
        <div class="nav-card-title">Risk Prediction</div>
        <div class="nav-card-desc">Enter patient vitals to get an ML-powered diabetes risk score and view prediction history.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="stat-row">
    <div class="stat-item">
        <div class="stat-value">47</div>
        <div class="stat-label">Counties Mapped</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">8</div>
        <div class="stat-label">Risk Features</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">ML</div>
        <div class="stat-label">Powered Model</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-value">Live</div>
        <div class="stat-label">Prediction Log</div>
    </div>
</div>
""", unsafe_allow_html=True)

# small disclaimer at the bottom — important for a health tool
st.markdown("""
<div class="info-strip">
    ℹ️ &nbsp;
    <span>
        This dashboard is for <b>analytical and educational purposes only</b>.
        Predictions are model-based estimates and should not replace clinical diagnosis
        by a qualified healthcare professional.
    </span>
</div>
""", unsafe_allow_html=True)