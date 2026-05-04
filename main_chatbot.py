import streamlit as st
import os
import json
from groq import Groq
# Už nepotřebujeme load_dotenv, pokud budeme používat st.secrets

# --- 1. NAČTENÍ KONFIGURACE BUSINESSU ---
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_config()

# --- 2. ZABEZPEČENÉ NASTAVENÍ KLÍČE ---
# Streamlit si klíč vytáhne ze skrytého souboru nebo z administrace cloudu
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# Nastavení vzhledu stránky podle businessu
st.set_page_config(page_title=data["name"], page_icon="🤖")
st.title(f"🤖 {data['name']} - Asistent")

# --- 3. SYSTEM PROMPT (To nejdůležitější pro prodej) ---
# Tímto říkáme AI, co je za firmu a co má odpovídat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": f"Jsi asistent pro {data['name']}. Info: {data['mission']}. Kontakt: {data['contact']}. Odpovídej stručně a mile."
        }
    ]

# Zobrazení historie (vynecháme systémovou instrukci)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Vstupní pole
if prompt := st.chat_input("Jak vám mohu pomoci?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Chyba: {e}")
            full_response = "Omlouvám se, spojení bylo přerušeno."

    st.session_state.messages.append({"role": "assistant", "content": full_response})