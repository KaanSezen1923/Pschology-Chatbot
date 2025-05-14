import streamlit as st
import pyodbc



conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=Chatbot;'
    'Trusted_Connection=yes;'
)

if conn is not  None:
    print("Connection successful")
else:
    print("Connection failed")
    
cursor= conn.cursor()


def login():
    with st.form("login"):
        email = st.text_input("Enter email")
        password = st.text_input("Enter password", type="password")  
        submit_button = st.form_submit_button("Login")
        if submit_button:
            if email and password:  
                try:
                    cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password))
                    user = cursor.fetchone()
                    if user is None:
                        st.error("Invalid email or password.")
                    else:
                        st.success("Login successful")
                        st.session_state["username"] =  user[1]  
                        st.switch_page("app.py")
                except Exception as e:
                    st.error(f"Error logging in: {e}")
            else:
                st.warning("Please fill in all fields.")
                
def signup():
    with st.form("signup"):
        username = st.text_input("Enter unique username")
        email = st.text_input("Enter email")
        password = st.text_input("Enter password", type="password")  
        submit_button = st.form_submit_button("Sign Up")
        if submit_button:
            if username and email and password:  
                try:
                    cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
                    conn.commit()
                    st.success("Sign up successful")
                    st.info("Please login with your email and password.")
                except Exception as e:
                    st.error(f"Error signing up: {e}")
            else:
                st.warning("Please fill in all fields.")


option = st.selectbox("Log in or Sign up", ("Log in", "Sign up"))

if option == "Log in":
    login()

else:
    signup()