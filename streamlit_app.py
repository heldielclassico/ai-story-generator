import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
st.title("🎓 Asisten Virtual Poltesa")

# Fungsi Reset Input
def clear_text():
    st.session_state["user_input"] = ""

# 3. Fungsi Load Prompt
def load_system_prompt(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    except Exception:
        return ""

# 4. Fungsi Generate Response dengan Fitur Counter
def generate_response(user_input):
    if not api_key:
        st.error("API Key tidak ditemukan di file .env!")
        return

    # Menggunakan model terbaru: gemini-2.0-flash
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    instruction = load_system_prompt("prompt.txt")
    
    final_prompt = f"""
    INSTRUCTIONS:
    {instruction}
    
    USER QUESTION:
    {user_input}
    
    YOUR ANSWER:
    """
    
    try:
        response = model.invoke(final_prompt)
        st.info(response.content)
    except Exception as e:
        error_msg = str(e)
        # Menangani Rate Limit (Error 429 / Resource Exhausted)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.warning("Batas penggunaan tercapai. Memulai pemulihan sistem...")
            
            # FITUR COUNTER: Hitung mundur 60 detik
            placeholder = st.empty()
            for seconds in range(60, 0, -1):
                placeholder.error(f"⏳ Gangguan Teknis (Limit). Mohon tunggu {seconds} detik sebelum bertanya lagi...")
                time.sleep(1)
            
            placeholder.success("✅ Sistem siap! Silakan klik 'Kirim Pertanyaan' kembali.")
        else:
            st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

# 5. UI Form
with st.form("chat_form"):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Halo Sobat Poltesa! Ada yang bisa saya bantu?",
        key="user_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submitted = st.form_submit_button("Kirim")
    with col2:
        # Tombol Clear menggunakan on_click
        st.form_submit_button("Hapus Chat", on_click=clear_text)
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            with st.spinner("Sivita sedang berpikir..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Update Data: 15 Desember 2025 | Sivita v2.0 (Gemini 2.0 Flash)")
