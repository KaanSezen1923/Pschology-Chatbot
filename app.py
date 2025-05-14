import streamlit as st
import requests
import pyodbc 
import datetime


api_url = "http://localhost:8000/ask" 
    
st.set_page_config(page_title="PsychologistGPT")
st.title("PsychologistGPT")

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

def generate_session_id():
    """Generate a unique session ID for grouping messages of the same conversation"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = generate_session_id()

def save_chat_to_db(user_id, messages, session_id=None):
    try:
        created_at = datetime.datetime.now()
        session_id = session_id or st.session_state.get("current_session_id", generate_session_id())
        
        for msg in messages:
            role = msg["role"]
            message_text = msg["content"]
            cursor.execute(
                "INSERT INTO chat_history (user_id, messages, created_at, role) VALUES (?, ?, ?, ?)",
                (user_id, message_text, created_at, role)
            )
        conn.commit()
    except Exception as e:
        st.error(f"Error saving chat to database: {e}")
        
def load_user_chats(user_id):
    try:
       
        cursor.execute("""
            SELECT chat_id, messages, created_at, role
            FROM chat_history 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        
        
        conversations = {}
        for row in rows:
            chat_id = row[0]
            message = row[1]
            created_at = row[2]
            role = row[3]
            
            
            timestamp_key = created_at.replace(microsecond=0)
            
           
            found_group = False
            for key in conversations.keys():
                if abs((timestamp_key - key).total_seconds()) < 10:
                    
                    conversations[key].append({
                        "chat_id": chat_id,
                        "message": message,
                        "created_at": created_at,
                        "role": role
                    })
                    found_group = True
                    break
            
            if not found_group:
               
                conversations[timestamp_key] = [{
                    "chat_id": chat_id,
                    "message": message,
                    "created_at": created_at,
                    "role": role
                }]
        
        
        chat_histories = {}
        for timestamp, message_group in conversations.items():
           
            chat_ids = [msg["chat_id"] for msg in message_group]
            conversation_id = str(min(chat_ids))
            
            
            sorted_messages = sorted(message_group, key=lambda x: x["created_at"])
            
            
            formatted_messages = [{"role": msg["role"], "content": msg["message"]} for msg in sorted_messages]
            
           
            chat_histories[conversation_id] = formatted_messages
            
        return chat_histories
    except Exception as e:
        st.error(f"Error loading user chats: {e}")
        return {}
    
def delete_chat_from_db(chat_ids):
    try:
        
        if not isinstance(chat_ids, list):
            chat_ids = [chat_ids]
            
      
        for chat_id in chat_ids:
            cursor.execute("DELETE FROM chat_history WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting chat from database: {e}")
        return False
        
        

    

    


if "message" not in st.session_state:
    st.session_state["message"] = []
    
for message in st.session_state["message"]:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    else:
        st.chat_message("assistant").markdown(message["content"])
        
if "username"  in st.session_state:
    username=st.session_state["username"] 
    st.subheader(f"Welcome {username}! How do you feel today?")
else:
    st.warning("Lütfen giriş yapın.")
    st.switch_page("pages/login.py")
    
if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {}
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = None
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = None
    

    
st.sidebar.title("Sohbet Geçmişi")

button_container = st.sidebar.container()
col1, col2 = button_container.columns([1, 1])

with col1:
    new_chat_button = st.button("Yeni Sohbet", use_container_width=True)
with col2:
    logout_button = st.button("Çıkış Yap", use_container_width=True)
    
user_id=cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,)).fetchone()[0]

if not st.session_state["chat_histories"]:
    st.session_state["chat_histories"] = load_user_chats(user_id)

if new_chat_button:
    st.session_state["current_chat"] = None
    st.session_state["message"] = []
    st.session_state["current_session_id"] = generate_session_id()
    st.rerun()


if logout_button:
    st.session_state.clear()
    st.switch_page("pages/login.py")


sorted_chat_histories = sorted(
    st.session_state["chat_histories"].items(),
    key=lambda x: x[0],
    reverse=True
)

for chat_id, chat_history in sorted_chat_histories:
    with st.sidebar.container():
       
        user_query_preview = "New chat"
        for msg in chat_history:
            if msg["role"] == "user":
                user_query_preview = msg["content"]
                break
                
        if len(user_query_preview) > 30:
            user_query_preview = user_query_preview[:27] + "..."

       
        

        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"{user_query_preview}", key=f"chat_{chat_id}"):
                st.session_state["current_chat"] = chat_id
                st.session_state["message"] = chat_history
                st.session_state["confirm_delete"] = None  
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                st.session_state["confirm_delete"] = chat_id
                st.rerun()

    if st.session_state["confirm_delete"] == chat_id:
        with st.sidebar.container():
            st.warning(f"'{user_query_preview}' sohbetini silmek istediğinize emin misiniz?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Evet, Sil", key=f"confirm_delete_{chat_id}"):
                   
                    chat_ids_to_delete = []
                    for msg in chat_history:
                        msg_chat_id = int(chat_id)  
                        if msg_chat_id not in chat_ids_to_delete:
                            chat_ids_to_delete.append(msg_chat_id)
                    
                    if delete_chat_from_db(chat_ids_to_delete):
                        st.session_state["chat_histories"].pop(chat_id, None)
                        
                        if st.session_state["current_chat"] == chat_id:
                            st.session_state["current_chat"] = None
                            st.session_state["message"] = []
                        
                        st.session_state["confirm_delete"] = None
                        st.success("Sohbet silindi.")
                        st.rerun()
            
            with col2:
                if st.button("İptal", key=f"cancel_delete_{chat_id}"):
                    st.session_state["confirm_delete"] = None
                    st.rerun()
    


user_query=st.chat_input("User: ")

if user_query:
    st.session_state["message"].append({"role": "user", "content": user_query})
    st.chat_message("user").markdown(user_query)
    
    response = requests.get(f"{api_url}/{user_query}")
    if response.status_code == 200:
        data = response.json()
        st.session_state["message"].append({"role": "assistant", "content": data["response"]})
        st.chat_message("assistant").markdown(data["response"])
        
       
        current_session_id = st.session_state.get("current_session_id")
        save_chat_to_db(user_id, [
            {"role": "user", "content": user_query}, 
            {"role": "assistant", "content": data["response"]}
        ], current_session_id)
        
        
        st.session_state["chat_histories"] = load_user_chats(user_id)
    else:
        st.error("Error: Unable to get a response from the API.")