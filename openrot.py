import streamlit as st
import os
import pandas as pd
import requests
import re
import time  # Tambahkan library time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. Load Environment Variables
load_dotenv()

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")

# --- FUNGSI VALIDASI EMAIL ---
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

# --- CSS KUSTOM ---
st.markdown("""
    <style>
    .stTextArea textarea { border-radius: 10px; }
    .stTextInput input { border-radius: 10px; }
    .stButton button { border-radius: 20px; }
    .stForm { margin-bottom: 0px !important; }
    .stCaption { margin-top: -15px !important; padding-top: 0px !important; }
    /* Gaya untuk informasi durasi */
    .duration-info {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: -10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Asisten Virtual Poltesa (Sivita)")

# --- FUNGSI: SIMPAN LOG KE GOOGLE SHEETS ---
def save_to_log(email, question, answer=""):
    try:
        log_url = st.secrets["LOG_URL"]
        payload = {"email": email, "question": question, "answer": answer}
        requests.post(log_url, json=payload, timeout=5)
    except Exception as e:
        print(f"Log Error: {e}")

# --- FUNGSI: AMBIL DATA GOOGLE SHEETS ---
def get_sheet_data():
    all_combined_data = ""
    try:     
        central_url = st.secrets["SHEET_CENTRAL_URL"]
        df_list = pd.read_csv(central_url)
        tab_names = df_list['NamaTab'].tolist()
        base_url = central_url.split('/export')[0]
        
        for tab in tab_names:
            tab_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={tab.replace(' ', '%20')}"
            try:
                df = pd.read_csv(tab_url)
                all_combined_data += f"\n\n### DATA {tab.upper()} ###\n{df.to_string(index=False)}"
            except:
                continue 
        return all_combined_data
    except:
        return ""

# --- FUNGSI: HAPUS CHAT ---
def clear_text():
    st.session_state["user_input"] = ""

# --- 4. Fungsi Generate Response dengan Timer ---
def generate_response(user_email, user_input):
    # Mulai hitung waktu
    start_time = time.time()
    
    try:
        api_key_secret = st.secrets["OPENROUTER_API_KEY"]
        instruction = st.secrets["SYSTEM_PROMPT"]
        
        # Proses ambil data (bagian yang memakan waktu)
        additional_data = get_sheet_data()
        
        model = ChatOpenAI(
            model="google/gemini-2.0-flash-lite-001",
            openai_api_key=api_key_secret,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.0
        )
        
        final_prompt = f"{instruction}\n\nDATA: {additional_data}\n\nPERTANYAAN: {user_input}\n\nJAWABAN:"
        
        try:
            response = model.invoke(final_prompt)
            
            # Hitung selisih waktu setelah jawaban didapat
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            if response and response.content:
                # Tampilkan info kecepatan
                st.markdown(f'<p class="duration-info">⏱️ Pencarian selesai dalam {duration} detik</p>', unsafe_allow_html=True)
                
                st.chat_message("assistant").markdown(response.content)
                save_to_log(user_email, user_input, response.content)
            else:
                st.warning("AI tidak dapat merumuskan jawaban.")
                
        except Exception as e:
            error_msg = str(e)
            if any(code in error_msg for code in ["429", "402"]):
                st.error("Mohon Maaf Kami sedang mengalami Gangguan Teknis. \n\n Web : https://poltesa.ac.id/")
            else:
                st.error(f"Terjadi kesalahan teknis: {e}")
                
    except Exception as e:
        st.error(f"Gagal memuat konfigurasi: {e}")

# 5. UI Form
with st.form("chat_form", clear_on_submit=False):
    user_email = st.text_input("Email Gmail Wajib:", placeholder="contoh@gmail.com", key="user_email")
    user_text = st.text_area("Tanyakan sesuatu tentang Poltesa:", placeholder="Halo! Saya Sivita...", key="user_input")
    
    col1, col2 = st.columns([1, 1]) 
    with col1:
        submitted = st.form_submit_button("Kirim", use_container_width=True)
    with col2:
        st.form_submit_button("Hapus Chat", on_click=clear_text, use_container_width=True)
    
    if submitted:
        if not user_email or not is_valid_email(user_email):
            st.error("Masukkan email @gmail.com yang valid!")
        elif user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan.")
        else:
            with st.spinner("Mencari data resmi..."):
                generate_response(user_email, user_text)

st.caption("Sivita - Sistem Informasi Virtual Asisten Poltesa @2025")
