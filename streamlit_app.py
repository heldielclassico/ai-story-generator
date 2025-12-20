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

    # Memuat konten prompt.txt
    instruction = load_system_prompt("prompt.txt")
    
    # Inisialisasi Model Gemini 2.5 Flash
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=api_key,
        temperature=0.0  # Wajib 0.0 agar jawaban tidak melebar/kreatif
    )
    
    # Teknik Grounding Ketat: Membatasi AI agar tidak menggunakan pengetahuan luar
    final_prompt = f"""
    SISTEM: 
    Anda adalah Sivita, Asisten Virtual resmi POLTESA. 
    Tugas Anda adalah menjawab pertanyaan pengguna HANYA berdasarkan DATA REFERENSI di bawah ini.

    DATA REFERENSI:
    ---
    {instruction}
    ---

    ATURAN KETAT:
    1. Gunakan HANYA informasi yang tersedia di DATA REFERENSI untuk menjawab.
    2. Jika pertanyaan pengguna tidak dapat dijawab menggunakan DATA REFERENSI, 
    jawablah: "Maaf, informasi tersebut saat ini tidak tersedia dalam database resmi kami Silakan cek di situs Resmi Poltesa : www.poltesa.ac.id"
    3. DILARANG memberikan jawaban berdasarkan pengetahuan umum atau data di luar teks di atas.
    4. Jawablah secara langsung, singkat, dan profesional.
    

    PERTANYAAN PENGGUNA: 
    {user_input}

    JAWABAN:
    """
    
    try:
        # Menghubungi Gemini
        response = model.invoke(final_prompt)
        
        # Validasi sederhana: Jika jawaban kosong atau error
        if response and response.content:
            st.info(response.content)
        else:
            st.warning("AI tidak dapat merumuskan jawaban berdasarkan data yang tersedia.")
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Silakan coba beberapa menit lagi. Anda juga dapat mengakses ke halaman Resmi POLTESA : www.poltesa.ac.id")
        else:
            st.error(f"Terjadi kesalahan teknis: {e}")

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











