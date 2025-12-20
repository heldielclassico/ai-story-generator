import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 2. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
st.title("🎓 Asisten Virtual Poltesa")

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

# 4. Fungsi Generate Response
def generate_response(user_input):
    if not api_key:
        st.error("API Key tidak ditemukan di file .env!")
        return

    # Memuat konten prompt.txt sebagai basis data utama AI
    instruction = load_system_prompt("prompt.txt")
    
    # Inisialisasi Model Gemini 2.5 Flash
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    # Menyusun instruksi ketat (System Instruction)
    final_prompt = f"""
    ROLE: Anda adalah Sivita, Asisten Virtual Resmi Politeknik Negeri Sambas (POLTESA).
    
    REFERENSI DATA WAJIB:
    {instruction}
    
    ATURAN JAWABAN:
    1. Anda WAJIB menjawab pertanyaan hanya berdasarkan REFERENSI DATA WAJIB di atas.
    2. Jika pertanyaan mengenai statistik (alumni, maba, prodi), gunakan data tepat sesuai referensi.
    3. Jika informasi TIDAK ADA dalam referensi, katakan dengan sopan bahwa data tersebut belum tersedia di database resmi saat ini.
    4. DILARANG berhalusinasi atau menggunakan informasi dari luar data yang diberikan.
    
    USER QUESTION:
    {user_input}
    
    YOUR ANSWER:
    """
    
    try:
        # Menghubungi Gemini
        response = model.invoke(final_prompt)
        st.info(response.content)
        
    except Exception as e:
        error_msg = str(e)
        # Jika limit tercapai, tampilkan hanya pesan error
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis (Limit Kuota). Silakan coba beberapa menit lagi.")
        else:
            st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

# 5. UI Form
with st.form("chat_form", clear_on_submit=False):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Halo Sobat Poltesa! Saya Sivita, ada yang bisa saya bantu hari ini?",
        key="user_input" 
    )
    
    # Kolom tombol agar sejajar di tampilan Mobile/HP
    col1, col2 = st.columns([1, 1.5]) 
    
    with col1:
        submitted = st.form_submit_button("Kirim", use_container_width=True)
    with col2:
        st.form_submit_button("Hapus Chat", on_click=clear_text, use_container_width=True)
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            with st.spinner("Mencari data resmi..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Database Internal Poltesa")
