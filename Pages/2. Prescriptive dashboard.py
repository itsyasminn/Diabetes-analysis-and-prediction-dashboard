import streamlit as st
import numpy as np
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime

best_model = joblib.load("best_diabetes_model.joblib")


importance_df = pd.DataFrame({
    'feature': ['Pregnancies','Glucose','BloodPressure','SkinThickness',
                'Insulin','BMI','DiabetesPedigreeFunction','Age'],
    'importance': best_model.named_steps['clf'].feature_importances_
})

# Database 
conn = sqlite3.connect("diabetes_predictions.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pregnancies INTEGER,
    glucose INTEGER,
    blood_pressure INTEGER,
    skin_thickness INTEGER,
    insulin INTEGER,
    bmi REAL,
    diabetes_pedigree_function REAL,
    age INTEGER,
    prediction INTEGER,
    probability REAL,
    timestamp DATETIME
)
''')
conn.commit()

# --- Page Title ---
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>Diabetes Prediction Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #34495E;'>Enter patient details to predict diabetes risk</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar Inputs ---
st.sidebar.header("Patient Information")
pregnancies = st.sidebar.number_input("Pregnancies", 0, 20, 2)
glucose = st.sidebar.number_input("Glucose", 0, 200, 120)
bp = st.sidebar.number_input("Blood Pressure", 0, 150, 70)
skin = st.sidebar.number_input("Skin Thickness", 0, 100, 35)
insulin = st.sidebar.number_input("Insulin", 0, 900, 100)
bmi = st.sidebar.number_input("BMI", 0.0, 60.0, 25.5)
dpf = st.sidebar.number_input("Diabetes Pedigree Function", 0.0, 2.5, 0.5, step=0.01)
age = st.sidebar.number_input("Age", 0, 120, 32)

predict_button = st.sidebar.button("Predict")

if predict_button:
    columns = ['Pregnancies','Glucose','BloodPressure','SkinThickness', 
               'Insulin','BMI','DiabetesPedigreeFunction','Age']
    data = pd.DataFrame([[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]], columns=columns)

    prediction = best_model.predict(data)[0]
    probability = best_model.predict_proba(data)[:,1][0]

    # --- Prediction Result ---
    st.subheader("Prediction Result")
    if prediction == 1:
        st.error("Prediction: Diabetes detected")
    else:
        st.success("Prediction: No Diabetes detected")
    st.info(f"Probability of having diabetes: {probability*100:.1f}%")
    st.subheader("Prediction Confidence")
    st.progress(int(probability*100))

    # --- Save to Database ---
    c.execute('''
        INSERT INTO predictions (
            pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi,
            diabetes_pedigree_function, age, prediction, probability, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pregnancies, glucose, bp, skin, insulin, bmi, dpf, age, prediction, probability, datetime.now()))
    conn.commit()

    # --- Pie Chart for Prediction ---
    st.subheader("Prediction Breakdown")
    labels = ['No Diabetes', 'Diabetes']
    sizes = [1-probability, probability]
    colors = ['#2ECC71','#E74C3C']
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

#  Feature Importance Chart 
st.subheader("Feature Importance")
plt.figure(figsize=(6,4))
sns.barplot(x='importance', y='feature', data=importance_df, palette="coolwarm")
plt.title("Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Feature")
st.pyplot(plt)

#  Prediction History 
st.subheader("Prediction History")
df_history = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
st.dataframe(df_history)

#  Comparison Histogram 
st.subheader("Probability Distribution of Past Predictions")
if not df_history.empty:
    plt.figure(figsize=(6,4))
    sns.histplot(df_history['probability'], bins=20, kde=True, color='#3498DB')
    plt.xlabel("Probability of Diabetes")
    plt.ylabel("Frequency")
    plt.title("Distribution of Prediction Probabilities")
    st.pyplot(plt)
