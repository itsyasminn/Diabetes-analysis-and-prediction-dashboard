import streamlit as st

st.set_page_config(
    page_title="Diabetes Prediction Dashboard",
    layout="wide"
)

st.title("Diabetes Prediction Dashboard")

st.markdown("""
Welcome to the Diabetes Analytics Dashboard.

Use the sidebar to navigate:

• **Descriptive Analysis** – County-level diabetes prevalence in Kenya  
• **Risk Prediction** – Predict diabetes risk using a machine learning model
""")
