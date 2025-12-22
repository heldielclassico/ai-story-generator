import streamlit as st
import os
import pandas as pd
import requests  # Library tambahan untuk mengirim log
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")

# --- CSS Kustom ---
st.markdown("""
    <style>
    .stTextArea textarea { border-radius: 10px; }
    .stButton button { border-radius: 20px; }
    a { word-wrap: break-word; text-decoration: none; color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Asisten Virtual Poltesa (Sivita)")

# --- FUNGSI BARU: SIMPAN LOG KE GOOGLE SHEETS ---
def save_to_log(question):
    """Mengirim pertanyaan user ke Google Apps Script untuk dicatat di sheet 'log'"""
    try:
        log_url = st.secrets["LOG_URL"]
        # Mengirim data pertanyaan dalam format JSON
        requests.post(log_url, json={"question": question}, timeout=5)
    except Exception as e:
        # Kita gunakan print agar error log tidak mengganggu tampilan user di UI
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
                all_combined_data += f"\n\n### DATA {tab.upper()} ###\n"
                all_combined_data += df.to_string(index=False)
            except:
                continue 
        return all_combined_data
    except Exception as e:
        return ""

# --- FUNGSI: CLEAR INPUT ---
def clear_text():
    st.session_state["user_input"] = ""

# 3. Fungsi Load Prompt
def load_system_prompt(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    except Exception as e:
        st.error(f"Gagal membaca file prompt: {e}")
        return ""

# --- 4. Fungsi Generate Response ---
def generate_response(user_input):
    try:
        api_key_secret = st.secrets["OPENROUTER_API_KEY"]
        instruction = st.secrets["SYSTEM_PROMPT"]
        additional_data = get_sheet_data()
    except KeyError:
        st.error("Konfigurasi Secrets tidak ditemukan!")
        return

    model = ChatOpenAI(
        model="google/gemini-2.5-flash-lite", # Versi terbaru/stabil di OpenRouter
        openai_api_key=api_key_secret,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0,
        default_headers={
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "Asisten Poltesa"            
        }
    )
    
    final_prompt = f"""
    {instruction}

    ### DATA TAMBAHAN DARI GOOGLE SHEETS ###
    {additional_data}

    ATURAN TAMBAHAN PEMFORMATAN:
    - Gunakan format [Nama Link](URL) untuk semua tautan agar rapi.
    - Jangan tampilkan URL mentah yang panjang.
    - Gunakan bullet points untuk daftar.

    PERTANYAAN PENGGUNA: 
    {user_input}

    JAWABAN:
    """
    
    try:
        response = model.invoke(final_prompt)
        if response and response.content:
            st.chat_message("assistant").markdown(response.content)
        else:
            st.warning("AI tidak dapat merumuskan jawaban.")
            
    except Exception as e:
        error_msg = str(e)
        if any(code in error_msg for code in ["429", "402"]):
            st.error("Mohon Maaf Kami sedang mengalami Gangguan Teknis. \n\n Web : https://poltesa.ac.id/")
        else:
            st.error(f"Terjadi kesalahan teknis: {e}")

# 5. UI Form
with st.form("chat_form", clear_on_submit=False):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Halo Sobat Poltesa! Saya Sivita, ada yang bisa saya bantu hari ini?",
        key="user_input" 
    )
    
    col1, col2 = st.columns([1, 1.5]) 
    
    with col1:
        submitted = st.form_submit_button("Kirim", use_container_width=True)
    with col2:
        st.form_submit_button("Hapus Chat", on_click=clear_text, use_container_width=True)
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            # --- PROSES SIMPAN LOG DIMULAI ---
            save_to_log(user_text)
            # --- PROSES SIMPAN LOG SELESAI ---
            
            with st.spinner("Mencari data resmi..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Database Internal Poltesa | Powered by OpenRouter")

