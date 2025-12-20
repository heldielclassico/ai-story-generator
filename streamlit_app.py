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

    # Load prompt.txt sebagai basis pengetahuan AI
    instruction = load_system_prompt("prompt.txt")
    
    # Inisialisasi Model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    # Final Prompt yang menekankan prompt.txt sebagai referensi utama
    final_prompt = f"""
    REFERENSI UTAMA (Gunakan data ini untuk menjawab):
    {instruction}
    
    PERTANYAAN PENGGUNA:
    {user_input}
    
    INSTRUKSI JAWABAN:
    1. Jawab berdasarkan REFERENSI UTAMA di atas.
    2. Jika data (seperti jumlah alumni, jurusan, dll) ada di referensi, gunakan data tersebut.
    3. Jika tidak ada di referensi, sampaikan bahwa informasi tersebut belum tersedia.
    
    JAWABAN ANDA:
    """
    
    try:
        # Menghubungi Gemini
        response = model.invoke(final_prompt)
        st.info(response.content)
        
    except Exception as e:
        error_msg = str(e)
        # Jika Gemini Limit, hanya tampilkan pesan error tanpa menampilkan isi prompt.txt
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis (Limit Kuota). Silakan coba beberapa menit lagi.")
        else:
            st.error(f"Terjadi kesalahan: {e}")

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
            with st.spinner("Menghubungi AI..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Database Internal Poltesa")

