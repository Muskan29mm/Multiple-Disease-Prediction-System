import streamlit as st
import mysql.connector
import re
import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
import pickle

# Setup MySQL connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql123",
    database="medical_database"
)

disease_precautions = {
    "Diabetes": [
        "Maintain a healthy diet and exercise regularly.",
        "Monitor blood sugar levels regularly.",
        "Manage stress through relaxation techniques.",
        "Take prescribed medications as directed."
    ],
    "Heart Disease": [
        "Eat a heart-healthy diet low in saturated fat and cholesterol.",
        "Engage in regular physical activity.",
        "Maintain a healthy weight.",
        "Manage stress effectively.",
        "Quit smoking and avoid secondhand smoke exposure.",
        "Take prescribed medications as directed."
    ],
    "Anemia": [
        "Eat iron-rich foods or take iron supplements as recommended by a doctor.",
        "Include foods rich in folate and vitamin B12 in your diet.",
        "Consider dietary changes to manage underlying conditions causing anemia.",
        "Take prescribed medications as directed if necessary.",
        "Get adequate rest."
    ]
}

# Functions for user authentication and patient data
def authenticate(FirstName, Password, LastName):
    cursor = db_connection.cursor()
    query = "SELECT * FROM patient WHERE FirstName = %s AND Password = %s AND LastName = %s"
    cursor.execute(query, (FirstName, Password, LastName))
    user = cursor.fetchone()
    cursor.close()
    return user

def add_user(FirstName, Password, LastName, Email, ContactNumber):
    cursor = db_connection.cursor()
    query = "INSERT INTO patient (FirstName, Password, LastName, Email, ContactNumber) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (FirstName, Password, LastName, Email, ContactNumber))
    db_connection.commit()
    cursor.close()

def add_patient_data(PatientID, FirstName, LastName, Age, Gender, ContactNumber, Address):
    cursor = db_connection.cursor()
    query = "INSERT INTO patient_data (PatientID, FirstName, LastName, Age, Gender, ContactNumber, Address, DateAdded, UpdatedAt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    date_added = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(query, (PatientID, FirstName, LastName, Age, Gender, ContactNumber, Address, date_added, date_added))
    db_connection.commit()
    cursor.close()

# Load models
diabetes_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/heart_disease_model.sav', 'rb'))
anemia_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/anemia_model.sav', 'rb'))


def predict_diabetes(Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age):
  # Load the diabetes prediction model
  diabetes_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/diabetes_model.sav', 'rb'))

  # Preprocess user input
  try:
    user_input = [float(x) for x in [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]]
  except ValueError:
    st.error("Please enter valid numerical values for all fields.")
    return None, None

  # Make prediction
  diab_prediction = diabetes_model.predict([user_input])

  # Return results
  if diab_prediction[0] == 1:
    disease = "Diabetes"
    precautions = disease_precautions.get(disease, [])
  else:
    disease = None
    precautions = []
  return disease, precautions


def predict_heart_disease(age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal):
    heart_disease_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/heart_disease_model.sav', 'rb'))
    
    try:
     user_input = [float(x) for x in [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
    except ValueError:
       st.error("Please enter valid numerical values for all fields.")
       return None, None

    heart_prediction = heart_disease_model.predict([user_input])
    if heart_prediction[0] == 1:
        disease = "Heart Disease"
        precautions = disease_precautions.get(disease, [])
    else:
        disease = None
        precautions = []
    return disease, precautions
   

def predict_anemia(Gender, Hemoglobin, MCH, MCHC, MCV):
    anemia_model = pickle.load(open('C:/Users/lenovo/Desktop/Multiple Disease Prediction System/Saved Models/anemia_model.sav', 'rb'))
    
    try:
     user_input = [float(x) for x in [Gender, Hemoglobin, MCH, MCHC, MCV]]
    except ValueError:
        st.error("Please enter valid numerical values for all fields.")
        return None, None
    
    anemia_prediction = anemia_model.predict([user_input])
    if anemia_prediction[0] == 1:
        disease = "Anemia"
        precautions = disease_precautions.get(disease, [])
    else:
        disease = None
        precautions = []
    return disease, precautions

# Streamlit app
st.write('<style>.stApp { background-color: #FFFFE0; }</style>', unsafe_allow_html=True)
# Pages
def login_page():
    st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
    st.header("**Login Page**")
    FirstName = st.text_input("**First Name**")
    Password = st.text_input("**Password**", type="password")
    LastName = st.text_input("**Last Name**")

    if st.button("**Login**"):
        if FirstName and Password and LastName:
            user = authenticate(FirstName, Password, LastName)
            if user:
                st.success("Logged in successfully!")
                st.session_state['logged_in'] = True
                st.session_state['FirstName'] = FirstName
                st.session_state['LastName'] = LastName
            else:
                st.error("Invalid FirstName, LastName or Password.")
        else:
            st.warning("Please enter all the fields.")

def signup_page():
    st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
    st.header("**Signup Page**")
    new_FirstName = st.text_input("**New First Name**")
    new_LastName = st.text_input("**New Last Name**")
    new_Email = st.text_input("**New Email**")
    new_Password = st.text_input("**New Password**", type="password")
    new_ContactNumber = st.text_input("**New Contact Number**")
    if st.button("**Signup**"):
        if new_FirstName and new_LastName and new_Password and new_Email:
            if (len(new_Password) >= 8 and
                re.search(r"\d", new_Password) and
                re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_Password)):
                add_user(new_FirstName, new_Password, new_LastName, new_Email, new_ContactNumber)
                st.success("Signup successful! You can now login.")
            else:
                st.warning("Password must be at least 8 characters long, contain a number and a special character.")
        else:
            st.warning("Please enter all the required fields.")

def patient_page():
    st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
    st.header("**Patient Data**")
    PatientID = st.text_input("**Patient ID**")
    FirstName = st.text_input("**First Name**")
    LastName = st.text_input("**Last Name**")
    Age = st.text_input("**Age**")
    Gender = st.radio("**Gender**", ("Male", "Female"))
    ContactNumber = st.text_input("**Contact Number**")
    Address = st.text_input("**Address**")
    if st.button("**Save**"):
        add_patient_data(PatientID, FirstName, LastName, Age, Gender, ContactNumber, Address)
        st.success("Patient data saved successfully!")

def disease_prediction_page():
    st.title('Multiple Disease Prediction System')
    selected = st.sidebar.radio(
        "Multiple Disease Prediction System",
        ['Diabetes Prediction', 'Heart Disease Prediction', 'Anemia Prediction']
    )

    if selected == 'Diabetes Prediction':
        st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
        st.header('Diabetes Prediction')
        Pregnancies = st.text_input('**Number of Pregnancies**')
        Glucose = st.text_input('**Glucose Level**')
        BloodPressure = st.text_input('**Blood Pressure**')
        SkinThickness = st.text_input('**Skin Thickness**')
        Insulin = st.text_input('**Insulin Level**')
        BMI = st.text_input('**BMI**')
        DiabetesPedigreeFunction = st.text_input('**Diabetes Pedigree Function**')
        Age = st.text_input('**Age**')
        
        predicted_disease, precautions = None, None
        
        if st.button('**Diabetes Test Result**'):
          # Call predict_diabetes only once and store the result
          predicted_disease, precautions = predict_diabetes(Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age)
          if predicted_disease:  # Check if disease is not None
              st.success(f"The person is diagnosed with {predicted_disease}.")
              if precautions:
                  st.subheader("Recommended Precautions:")
                  for precaution in precautions:
                      st.write("- " + precaution)
          else:
              st.success("The person is unlikely to have Diabetes.")
           
             
              
              
        
        result_df = pd.DataFrame({'Result': [predicted_disease]})
        result_csv = result_df.to_csv(index=False)
        st.download_button(
            label="**Download Result as CSV**",
            data=result_csv,
            file_name="diabetes_prediction_result.csv",
            mime="text/csv"
               )
  
    elif selected == 'Heart Disease Prediction':
        st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
        st.header('Heart Disease Prediction')
        age = st.text_input('**Age**')
        sex = st.text_input('**Sex**')
        cp = st.text_input('**Chest Pain types**')
        trestbps = st.text_input('**Resting Blood Pressure**')
        chol = st.text_input('**Serum Cholestoral (mg/dl)**')
        fbs = st.text_input('**Fasting Blood Sugar > 120 mg/dl**')
        restecg = st.text_input('**Resting Electrocardiographic results**')
        thalach = st.text_input('**Maximum Heart Rate achieved**')
        exang = st.text_input('**Exercise Induced Angina**')
        oldpeak = st.text_input('**ST depression induced by exercise**')
        slope = st.text_input('**Slope of the peak exercise ST segment**')
        ca = st.text_input('**Major vessels colored by flourosopy**')
        thal = st.text_input('**Thal: 0 = normal, 1 = fixed defect, 2 = reversable defect**')
        
        predicted_disease, precautions = None, None
        
        if st.button('**Heart Disease Test Result**'):
            predicted_disease, precautions = predict_heart_disease(age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal)
            if predicted_disease:
                st.success('The person has Heart Disease')
                if precautions:
                    st.subheader("Recommended Precautions:")
                    for precaution in precautions:
                        st.write("- " + precaution)
            else:
                st.success('The person does not have heart disease')
                
        
        result_df = pd.DataFrame({'Result': [predicted_disease]})
        result_csv = result_df.to_csv(index=False)
        st.download_button(
            label="**Download Result as CSV**",
            data=result_csv,
            file_name="heart_prediction_result.csv",
            mime="text/csv"
              )
  

    elif selected == 'Anemia Prediction':
        st.write('<style>input[type="text"], input[type="password"] { background-color: #FFFFC2; color: #000000; }</style>', unsafe_allow_html=True)
        st.header('Anemia Prediction')
        Gender = st.text_input('**Gender**')
        Hemoglobin = st.text_input('**Hemoglobin**')
        MCH = st.text_input('**MCH**')
        MCHC = st.text_input('**MCHC**')
        MCV = st.text_input('**MCV**')
        
        predicted_disease, precautions = None, None
        
        if st.button('**Anemia Test Result**'):
            predicted_disease, precautions = predict_anemia(Gender, Hemoglobin, MCH, MCHC, MCV)
            if predicted_disease:
                st.success('The person is having Anemia')
                if precautions:
                    st.subheader("Recommended Precautions:")
                    for precaution in precautions:
                        st.write("- " + precaution)
            else:
                st.success('The person does not have Anemia')
                
        result_df = pd.DataFrame({'Result': [predicted_disease]})
        result_csv = result_df.to_csv(index=False)
        st.download_button(
            label="**Download Result as CSV**",
            data=result_csv,
            file_name="anemia_prediction_result.csv",
            mime="text/csv"
               )

navigation_panel_style = """
<style>
  [data-testid="stSidebar"] {
    background-color: #FAFAD2;  /* Change this to your desired color */
    color: black;  /* Optional: Set text color for the panel */
    font-size: 120px;
  }
</style>
"""
st.write(navigation_panel_style, unsafe_allow_html=True)

# Main function
def main():
    st.write('<style>.stContainer { background-color: #FFFFE0; }</style>', unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    menu = ["Login", "Sign Up", "Patient Data", "Disease Prediction"]
    choice = st.sidebar.selectbox("Menu", menu)

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if choice == "Login":
        login_page()
    elif choice == "Sign Up":
        signup_page()
    elif choice == "Patient Data":
        if st.session_state['logged_in']:
            patient_page()
        else:
            st.warning("Please login to access this page.")
    elif choice == "Disease Prediction":
        if st.session_state['logged_in']:
            disease_prediction_page()
        else:
            st.warning("Please login to access this page.")

if __name__ == '__main__':
    main()
