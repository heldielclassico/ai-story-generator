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

# 4. Fungsi Generate Response (Prioritas Lokal -> Gemini)
def generate_response(user_input):
    if not api_key:
        st.error("API Key tidak ditemukan di file .env!")
        return

    instruction = load_system_prompt("prompt.txt")
    
    # --- ALUR 1: CEK DATA LOKAL (PROMPT.TXT) ---
    found_locally = False
    if instruction:
        lines = instruction.split('\n')
        # Mencari baris tanggal update
        update_info = next((line for line in lines if "Update" in line), "")
        
        # Daftar kata kunci yang sering ditanyakan (Statistik)
        keywords = ["alumni", "mahasiswa", "prodi", "dosen", "tendik", "penelitian", "kerjasama", "pkm"]
        user_query_lower = user_input.lower()
        
        relevant_info = []
        for line in lines:
            # Cek apakah ada kata kunci yang cocok di baris prompt.txt
            for key in keywords:
                if key in user_query_lower and key in line.lower():
                    relevant_info.append(line)
                    found_locally = True
                    break # Lanjut ke baris berikutnya jika sudah ketemu 1 keyword yang cocok

        # Jika data ditemukan di lokal, langsung tampilkan dan berhenti (Return)
        if found_locally:
            if update_info:
                st.write(f"**{update_info}**")
            for info in relevant_info:
                st.info(info)
            return 

    # --- ALUR 2: JIKA TIDAK ADA DI LOKAL, GUNAKAN GEMINI ---
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
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
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Silakan coba beberapa menit lagi.")
            # Opsi: Jika Gemini limit, tampilkan seluruh isi prompt sebagai fallback terakhir
            with st.expander("Klik untuk melihat semua data informasi Poltesa"):
                st.write(instruction)
        else:
            st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

# 5. UI Form
with st.form("chat_form", clear_on_submit=False):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Halo Sobat Poltesa! Saya Sivita, ada yang bisa saya bantu?",
        key="user_input" 
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        submitted = st.form_submit_button("Kirim")
    with col2:
        clear_button = st.form_submit_button("Hapus Chat", on_click=clear_text)
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            with st.spinner("Mencari data resmi..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Database Internal Poltesa")
