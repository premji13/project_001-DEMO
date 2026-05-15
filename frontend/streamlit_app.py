import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="User Auth", layout="centered")

st.title("User Authentication")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

tabs = st.tabs(["Register", "Login"])

with tabs[0]:
    st.header("Register")
    with st.form("register_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")
    if submitted:
        payload = {"email": email, "username": username, "password": password}
        try:
            resp = requests.post(f"{BASE_URL}/users/register", json=payload, timeout=10)
            if resp.status_code == 201:
                st.success("Registered successfully. OTP sent to your email.")
                st.json(resp.json())
            else:
                st.error(f"Registration failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Error contacting API: {e}")

with tabs[1]:
    st.header("Login")
    with st.form("login_form"):
        email_l = st.text_input("Email", key="login_email")
        password_l = st.text_input("Password", type="password", key="login_password")
        login_sub = st.form_submit_button("Login")
    if login_sub:
        payload = {"email": email_l, "password": password_l}
        try:
            resp = requests.post(f"{BASE_URL}/users/login", json=payload, timeout=10)
            if resp.status_code == 200:
                st.success("Login successful")
                data = resp.json()
                st.write("Access token:")
                st.code(data.get("access_token",""))
                st.write("User:")
                st.json(data.get("user"))
            else:
                st.error(f"Login failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Error contacting API: {e}")


st.write("\n---\n")
st.write("This Streamlit app is a simple UI to register and login users using the FastAPI backend.")