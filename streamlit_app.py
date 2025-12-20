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

# --- FUNGSI BARU: CLEAR INPUT ---
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

    instruction = load_system_prompt("prompt.txt")
    
    # --- PRIORITAS 1: PENCARIAN MANUAL DI PROMPT.TXT ---
    found_locally = False
    if instruction:
        lines = instruction.split('\n')
        update_info = next((line for line in lines if "Update" in line), "")
        
        # Mencari kata kunci penting dari input user (misal: "alumni", "mahasiswa", "prodi")
        keywords = ["alumni", "mahasiswa", "prodi", "dosen", "tendik", "penelitian", "kerjasama", "pkm"]
        user_query_lower = user_input.lower()
        
        relevant_info = []
        for line in lines:
            # Jika baris mengandung kata kunci yang ditanyakan user
            for key in keywords:
                if key in user_query_lower and key in line.lower():
                    relevant_info.append(line)
                    found_locally = True

        # Jika ditemukan di prompt.txt, tampilkan hasilnya
        if found_locally:
            if update_info:
                st.write(f"**{update_info}**")
            for info in relevant_info:
                st.info(info)
            return  # Berhenti di sini, tidak perlu panggil Gemini

    # --- PRIORITAS 2: JIKA TIDAK ADA DI PROMPT.TXT, BARU PAKAI GEMINI ---
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    final_prompt = f"INSTRUCTIONS:\n{instruction}\n\nUSER QUESTION:\n{user_input}\n\nYOUR ANSWER:"
    
    try:
        response = model.invoke(final_prompt)
        st.info(response.content)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Silakan coba beberapa menit lagi.")
        else:
            st.error(f"Terjadi kesalahan: {e}")

# 5. UI Form
# Menggunakan key="user_input" agar bisa diakses oleh fungsi clear_text
with st.form("chat_form", clear_on_submit=False):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Halo Sobat Poltesa! Saya Sivita, Asisten Virtual Resmi Politeknik Negeri Sambas. Ada yang bisa saya bantu hari ini?",
        key="user_input" 
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submitted = st.form_submit_button("Kirim")
    with col2:
        # Tombol Clear menggunakan on_click untuk mereset session state
        clear_button = st.form_submit_button("Hapus Chat", on_click=clear_text)
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            with st.spinner("Mencari data resmi..."):
                generate_response(user_text)

# Footer sederhana
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Quipper Campus")

