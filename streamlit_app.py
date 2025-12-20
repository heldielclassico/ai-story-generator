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

# 3. Fungsi Load Prompt
def load_system_prompt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"File {file_path} tidak ditemukan!")
        return ""

# 4. Fungsi Generate Response
def generate_response(user_input):
    if not api_key:
        st.error("API Key tidak ditemukan di file .env!")
        return

    # Inisialisasi Model dengan Temperature 0 (Sangat Kaku)
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    # Ambil instruksi dari file txt
    instruction = load_system_prompt("prompt.txt")
    
    # Teknik Gabungkan instruksi dan input user dalam satu string (Prompt Engineering)
    # Ini memaksa model membaca data instruksi tepat sebelum menjawab
    final_prompt = f"""
    INSTRUCTIONS:
    {instruction}
    
    USER QUESTION:
    {user_input}
    
    YOUR ANSWER:
    """
    
    try:
        response = model.invoke(final_prompt)
        # Menampilkan hasil dengan kotak informasi
        st.info(response.content)
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

# 5. UI Form
with st.form("chat_form"):
    user_text = st.text_area(
        "Tanyakan sesuatu tentang Poltesa:",
        placeholder="Siapa direktur Poltesa?"
    )
    submitted = st.form_submit_button("Kirim Pertanyaan")
    
    if submitted:
        if user_text.strip() == "":
            st.warning("Mohon masukkan pertanyaan terlebih dahulu.")
        else:
            with st.spinner("Mencari data resmi..."):
                generate_response(user_text)

# Footer sederhana
st.markdown("---")
st.caption("Sumber data: poltesa.ac.id & Quipper Campus")
