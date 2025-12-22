import streamlit as st
import os
import pandas as pd
import requests
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. Load Environment Variables
load_dotenv()

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")

# Inisialisasi State
if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = ""
if "should_clear" not in st.session_state:
    st.session_state["should_clear"] = False
if "saved_email" not in st.session_state:
    st.session_state["saved_email"] = ""

# --- FUNGSI VALIDASI EMAIL ---
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

# --- FUNGSI: SIMPAN LOG ---
def save_to_log(email, question, answer=""):
    try:
        log_url = st.secrets["LOG_URL"]
        payload = {"email": email, "question": question, "answer": answer}
        requests.post(log_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Log Error: {e}")

# --- FUNGSI: AMBIL DATA ---
def get_sheet_data():
    try:     
        central_url = st.secrets["SHEET_CENTRAL_URL"]
        df_list = pd.read_csv(central_url)
        tab_names = df_list['NamaTab'].tolist()
        base_url = central_url.split('/export')[0]
        all_data = ""
        for tab in tab_names:
            tab_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={tab.replace(' ', '%20')}"
            try:
                df = pd.read_csv(tab_url)
                all_data += f"\n\n### DATA {tab.upper()} ###\n{df.to_string(index=False)}"
            except: continue 
        return all_data
    except: return ""

# --- FUNGSI: GENERATE RESPONSE ---
def generate_response(user_email, user_input):
    try:
        api_key_secret = st.secrets["OPENROUTER_API_KEY"]
        instruction = st.secrets["SYSTEM_PROMPT"]
        additional_data = get_sheet_data()
        
        model = ChatOpenAI(
            model="google/gemini-2.5-flash-lite",
            openai_api_key=api_key_secret,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.0
        )
        
        final_prompt = f"{instruction}\n\nDATA: {additional_data}\n\nPERTANYAAN: {user_input}\n\nJAWABAN:"
        response = model.invoke(final_prompt)
        
        if response and response.content:
            st.session_state["last_answer"] = response.content
            save_to_log(user_email, user_input, response.content)
            return response.content
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")
        return None

# --- LOGIKA AUTO-CLEAR SAAT JAWABAN SUDAH ADA ---
def on_text_change():
    # Jika user mulai mengetik dan sebelumnya sudah ada jawaban, kosongkan textarea
    if st.session_state["should_clear"]:
        st.session_state["user_input_widget"] = ""
        st.session_state["should_clear"] = False

st.title("🎓 Asisten Virtual Poltesa (Sivita)")

# --- UI FORM ---
with st.form("chat_form", clear_on_submit=False):
    user_email = st.text_input(
        "Email Gmail Wajib:", 
        placeholder="contoh@gmail.com",
        value=st.session_state["saved_email"]
    )
    
    # Textarea dengan callback on_change
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Ketik pertanyaan di sini...",
        key="user_input_widget",
        on_change=on_text_change
    )
    
    submitted = st.form_submit_button("Kirim", use_container_width=True)

# Logika Eksekusi
if submitted:
    if not user_email or not is_valid_email(user_email):
        st.error("Format email harus nama@gmail.com")
    elif user_text.strip() == "":
        st.warning("Masukkan pertanyaan.")
    else:
        st.session_state["saved_email"] = user_email
        with st.spinner("Mencari data resmi..."):
            generate_response(user_email, user_text)
            # Tandai bahwa setelah ini, jika user klik textarea lagi, teks harus hilang
            st.session_state["should_clear"] = True
            st.rerun()

# --- AREA TAMPILAN JAWABAN ---
if st.session_state["last_answer"]:
    st.write("---")
    st.chat_message("assistant").markdown(st.session_state["last_answer"])

st.markdown("---")
st.caption("Sivita - Sistem Informasi Virtual Asisten Poltesa")
