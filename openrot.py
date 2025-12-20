import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 1. Load Environment Variables
load_dotenv()
# Pastikan di file .env variabelnya adalah OPENROUTER_API_KEY
api_key = os.getenv("OPENROUTER_API_KEY")

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
st.title("🎓 Asisten Virtual Poltesa (Sivita)")

# --- FUNGSI: CLEAR INPUT ---
def clear_text():
    st.session_state["user_input"] = ""

# 3. Fungsi Load Prompt
def load_system_prompt(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            st.error(f"File {file_path} tidak ditemukan!")
            return ""
    except Exception as e:
        st.error(f"Gagal membaca file prompt: {e}")
        return ""

# --- 4. Fungsi Generate Response (Menggunakan st.secrets) ---
def generate_response(user_input):
    # Mengambil API Key dan Prompt dari Streamlit Secrets secara aman
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
        instruction = st.secrets["SYSTEM_PROMPT"]
    except KeyError:
        st.error("Konfigurasi Secrets (API Key atau Prompt) tidak ditemukan!")
        return

    # Inisialisasi Model melalui OpenRouter
    model = ChatOpenAI(
        model="google/gemini-2.5-flash-lite", 
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0,
        default_headers={
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "Asisten Poltesa"            
        }
    )
    
    # Teknik Grounding Ketat dengan data dari Secrets
    final_prompt = f"""
    {instruction}

    PERTANYAAN PENGGUNA: 
    {user_input}

    JAWABAN:
    """
    
    try:
        # Menghubungi OpenRouter
        response = model.invoke(final_prompt)
        
        if response and response.content:
            st.info(response.content)
        else:
            st.warning("AI tidak dapat merumuskan jawaban berdasarkan data yang tersedia.")
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            st.error("Limit API tercapai atau saldo OpenRouter habis. Silakan cek akun Anda.")
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
            with st.spinner("Mencari data resmi di database Poltesa..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Database Internal Poltesa | Powered by OpenRouter")



