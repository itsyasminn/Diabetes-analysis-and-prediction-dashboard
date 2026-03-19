import streamlit as st
import numpy as np
import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime
 
st.set_page_config(page_title="Risk Prediction", page_icon="🤖", layout="wide")
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');
 
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}
 
.stApp {
    background: #0a1628;
}
 
.page-tag {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #00c8b4;
    margin-bottom: 8px;
}
 
.page-title {
    font-size: 36px;
    font-weight: 700;
    color: #e8f0f8;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
 
.page-desc {
    font-size: 14px;
    color: #667788;
    max-width: 500px;
    margin-bottom: 32px;
}
 
.result-card {
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
}
 
.result-card.positive {
    background: rgba(231, 76, 60, 0.08);
    border: 1px solid rgba(231, 76, 60, 0.3);
}
 
.result-card.negative {
    background: rgba(39, 174, 96, 0.08);
    border: 1px solid rgba(39, 174, 96, 0.3);
}
 
.result-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
 
.result-label.positive { color: #e74c3c; }
.result-label.negative { color: #27ae60; }
 
.result-main {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 6px;
}
 
.result-main.positive { color: #e74c3c; }
.result-main.negative { color: #2ecc71; }
 
.result-prob {
    font-size: 14px;
    color: #8899aa;
}
 
.result-prob span {
    font-family: 'Space Mono', monospace;
    color: #aabbc8;
    font-weight: 700;
}
 
.risk-bar-wrap {
    margin-top: 16px;
}
 
.risk-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #556677;
    margin-bottom: 6px;
}
 
.section-title {
    font-size: 18px;
    font-weight: 600;
    color: #ccd8e4;
    margin: 0 0 4px 0;
}
 
.section-sub {
    font-size: 12px;
    color: #556677;
    margin-bottom: 18px;
}
 
.divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 28px 0;
}
 
.input-hint {
    background: rgba(0,200,180,0.05);
    border: 1px solid rgba(0,200,180,0.12);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12px;
    color: #6688aa;
    line-height: 1.6;
    margin-bottom: 24px;
}
 
.history-empty {
    text-align: center;
    padding: 40px 20px;
    color: #445566;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)
 
# Load model & DB 
@st.cache_resource
def load_model():
    return joblib.load("best_diabetes_model.joblib")
 
best_model = load_model()
 
importance_df = pd.DataFrame({
    'Feature': ['Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness',
                'Insulin', 'BMI', 'Diabetes Pedigree Fn.', 'Age'],
    'Importance': best_model.named_steps['clf'].feature_importances_
}).sort_values('Importance', ascending=True)
 
conn = sqlite3.connect("diabetes_predictions.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pregnancies INTEGER, glucose INTEGER, blood_pressure INTEGER,
    skin_thickness INTEGER, insulin INTEGER, bmi REAL,
    diabetes_pedigree_function REAL, age INTEGER,
    prediction INTEGER, probability REAL, timestamp DATETIME
)''')
conn.commit()
 
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8899aa", family="Sora"),
    margin=dict(l=0, r=0, t=10, b=10),
)
 
# Page Header 
st.markdown("""
<div>
    <div class="page-tag">🤖 Page 2</div>
    <div class="page-title">Risk Prediction</div>
    <div class="page-desc">Enter patient vitals to get an ML-powered diabetes risk score.</div>
</div>
""", unsafe_allow_html=True)
 
# Sidebar Inputs
with st.sidebar:
    st.markdown("### 🩺 Patient Information")
    st.markdown('<div class="input-hint">Adjust the values below to match patient measurements, then click <b>Run Prediction</b>.</div>', unsafe_allow_html=True)
 
    pregnancies = st.slider("Pregnancies", 0, 20, 2)
    glucose     = st.slider("Glucose (mg/dL)", 0, 200, 120)
    bp          = st.slider("Blood Pressure (mmHg)", 0, 150, 70)
    skin        = st.slider("Skin Thickness (mm)", 0, 100, 35)
    insulin     = st.slider("Insulin (μU/mL)", 0, 900, 100)
    bmi         = st.slider("BMI", 0.0, 60.0, 25.5, step=0.1)
    dpf         = st.slider("Diabetes Pedigree Function", 0.0, 2.5, 0.5, step=0.01)
    age         = st.slider("Age (years)", 1, 120, 32)
 
    st.markdown("---")
    predict_button = st.button("▶  Run Prediction", use_container_width=True, type="primary")
 
# Layout: Result + Charts 
left_col, right_col = st.columns([1, 1], gap="large")
 
with left_col:
    if predict_button:
        cols = ['Pregnancies','Glucose','BloodPressure','SkinThickness',
                'Insulin','BMI','DiabetesPedigreeFunction','Age']
        data = pd.DataFrame([[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]], columns=cols)
        prediction  = best_model.predict(data)[0]
        probability = best_model.predict_proba(data)[:,1][0]
 
        # Save to DB
        c.execute('''INSERT INTO predictions
            (pregnancies,glucose,blood_pressure,skin_thickness,insulin,bmi,
             diabetes_pedigree_function,age,prediction,probability,timestamp)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
            (pregnancies,glucose,bp,skin,insulin,bmi,dpf,age,
             int(prediction),float(probability),datetime.now()))
        conn.commit()
 
        # Result card
        card_class = "positive" if prediction == 1 else "negative"
        icon   = "⚠️" if prediction == 1 else "✅"
        label  = "DIABETES DETECTED" if prediction == 1 else "NO DIABETES DETECTED"
        st.markdown(f"""
        <div class="result-card {card_class}">
            <div class="result-label {card_class}">{icon} Prediction Result</div>
            <div class="result-main {card_class}">{label}</div>
            <div class="result-prob">Risk probability: <span>{probability*100:.1f}%</span></div>
            <div class="risk-bar-wrap">
                <div class="risk-bar-label"><span>Low Risk</span><span>High Risk</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(probability * 100))
 
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(probability * 100, 1),
            number={"suffix": "%", "font": {"size": 32, "color": "#e0eaf4", "family": "Space Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#445566", "tickfont": {"color": "#445566"}},
                "bar": {"color": "#e74c3c" if prediction == 1 else "#27ae60"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(39,174,96,0.12)"},
                    {"range": [40, 70], "color": "rgba(243,156,18,0.12)"},
                    {"range": [70, 100], "color": "rgba(231,76,60,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#f39c12", "width": 2},
                    "thickness": 0.75,
                    "value": 50,
                },
            },
            title={"text": "Diabetes Risk Score", "font": {"color": "#667788", "size": 13, "family": "Sora"}},
        ))
        layout = {**PLOTLY_LAYOUT, 'margin': dict(l=20, r=20, t=30, b=10)}
        fig_gauge.update_layout(
    **layout,
    height=280,
)
        st.plotly_chart(fig_gauge, use_container_width=True)
 
        # Donut chart
        fig_donut = go.Figure(go.Pie(
            labels=["No Diabetes", "Diabetes"],
            values=[1 - probability, probability],
            hole=0.6,
            marker=dict(colors=["rgba(39,174,96,0.7)", "rgba(231,76,60,0.7)"],
                        line=dict(color="#0a1628", width=3)),
            textfont=dict(family="Sora", size=12, color="#aabbcc"),
        ))
        fig_donut.update_layout(
            **PLOTLY_LAYOUT,
            height=260,
            legend=dict(font=dict(color="#8899aa"), orientation="h", yanchor="bottom", y=-0.15),
            annotations=[dict(text=f"{probability*100:.1f}%", font=dict(size=22, color="#e0eaf4", family="Space Mono"), showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
 
    else:
        st.markdown("""
        <div style="text-align:center; padding:80px 20px; color:#334455;">
            <div style="font-size:48px; margin-bottom:16px;">🩺</div>
            <div style="font-size:15px; font-weight:600; color:#445566; margin-bottom:8px;">No prediction yet</div>
            <div style="font-size:13px; color:#334455; line-height:1.6;">Adjust the patient vitals in the<br>sidebar and click <b style="color:#445566">Run Prediction</b>.</div>
        </div>
        """, unsafe_allow_html=True)
 
with right_col:
    # Feature importance
    st.markdown('<div class="section-title">🔍 Feature Importance</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">How much each feature contributes to the model</div>', unsafe_allow_html=True)
 
    fig_imp = px.bar(
        importance_df, x="Importance", y="Feature", orientation="h",
        color="Importance",
        color_continuous_scale="Teal",
    )
    fig_imp.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11, color="#aabbcc")),
        height=320,
    )
    st.plotly_chart(fig_imp, use_container_width=True)
 
    # Input radar chart
    st.markdown('<div class="section-title">🕸️ Patient Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Normalised vitals vs typical range</div>', unsafe_allow_html=True)
 
    ranges = {'Pregnancies':20,'Glucose':200,'BloodPressure':150,
              'SkinThickness':100,'Insulin':900,'BMI':60,'DiabetesPedigreeFunction':2.5,'Age':120}
    vals = [pregnancies/20, glucose/200, bp/150, skin/100,
            insulin/900, bmi/60, dpf/2.5, age/120]
    labels = ['Preg.','Glucose','BP','Skin','Insulin','BMI','DPF','Age']
 
    fig_radar = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=labels + [labels[0]],
        fill='toself',
        fillcolor='rgba(0,200,180,0.1)',
        line=dict(color='#00c8b4', width=2),
        name='Patient',
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[0.5]*len(labels) + [0.5],
        theta=labels + [labels[0]],
        mode='lines',
        line=dict(color='rgba(243,156,18,0.4)', width=1.5, dash='dot'),
        name='Midpoint Ref.',
    ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899aa", family="Sora"),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,1], color="#334455",
                            gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=9)),
            angularaxis=dict(color="#8899aa", gridcolor="rgba(255,255,255,0.06)",
                             tickfont=dict(size=11))
        ),
        legend=dict(font=dict(color="#8899aa"), orientation="h", y=-0.1),
        height=340,
        margin=dict(l=20, r=20, t=10, b=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)
 
#  Prediction History 
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Prediction History</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">All past predictions logged in this session</div>', unsafe_allow_html=True)
 
df_history = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
 
if df_history.empty:
    st.markdown('<div class="history-empty">No predictions logged yet. Run a prediction to start tracking.</div>', unsafe_allow_html=True)
else:
    # Summary metrics
    h1, h2, h3, h4 = st.columns(4)
    total   = len(df_history)
    pos_pct = (df_history['prediction'] == 1).mean() * 100
    avg_prob= df_history['probability'].mean() * 100
    last_ts = pd.to_datetime(df_history['timestamp'].iloc[0]).strftime("%d %b %H:%M")
 
    for col, val, lbl in zip([h1,h2,h3,h4],
        [total, f"{pos_pct:.1f}%", f"{avg_prob:.1f}%", last_ts],
        ["Total Predictions","Positive Rate","Avg Probability","Last Recorded"]):
        col.metric(lbl, val)
 
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
 
    # Probability distribution
    col_a, col_b = st.columns(2)
    with col_a:
        fig_ph = px.histogram(
            df_history, x='probability', nbins=15,
            color_discrete_sequence=['#00c8b4'],
            labels={'probability': 'Diabetes Probability', 'count': 'Count'},
            marginal='rug',
        )
        fig_ph.update_layout(**PLOTLY_LAYOUT,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=".0%"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            height=280, title_text="Probability Distribution",
            title_font=dict(color="#8899aa", size=13))
        st.plotly_chart(fig_ph, use_container_width=True)
 
    with col_b:
        fig_scatter = px.scatter(
            df_history.reset_index(), x='id', y='probability',
            color='prediction',
            color_discrete_map={0: '#27ae60', 1: '#e74c3c'},
            labels={'id':'Prediction #','probability':'Risk Probability','prediction':'Outcome'},
            symbol='prediction',
        )
        fig_scatter.update_layout(**PLOTLY_LAYOUT,
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=".0%"),
            height=280, title_text="Predictions Over Time",
            title_font=dict(color="#8899aa", size=13),
            legend=dict(font=dict(color="#8899aa")))
        st.plotly_chart(fig_scatter, use_container_width=True)
 
    # Table
    with st.expander(" View Full Log"):
        display_cols = ['id','pregnancies','glucose','blood_pressure','bmi','age','prediction','probability','timestamp']
        df_show = df_history[display_cols].copy()
        df_show['probability'] = (df_show['probability']*100).round(1).astype(str) + '%'
        df_show['prediction']  = df_show['prediction'].map({0:'✅ No Diabetes','1':'⚠️ Diabetes',1:'⚠️ Diabetes'})
        st.dataframe(df_show, use_container_width=True, height=350)
 