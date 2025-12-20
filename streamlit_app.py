import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
# IMPORT FUNGSI DARI FILE SEBELAH
from scraper import get_data_kerjasama

# Memuat variabel dari file .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def load_system_prompt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Anda adalah asisten virtual POLTESA."

st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
st.title("🎓 Asisten Virtual Poltesa")

def generate_response(input_text):
    if not api_key:
        st.error("API Key tidak ditemukan!")
        return

    # 1. Panggil fungsi dari scraper.py
    data_tambahan = get_data_kerjasama()
    
    # 2. Ambil instruksi dasar
    instruction_base = load_system_prompt("prompt.txt")
    
    # 3. Gabungkan instruksi dengan data scraping agar AI tahu
    full_instruction = f"{instruction_base}\n\nBerikut adalah data mitra kerjasama terbaru:\n{data_tambahan}"

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite", # Gunakan 1.5 flash jika 2.5 belum tersedia di library Anda
        google_api_key=api_key,
        temperature=0.0
    )
    
    messages = [
        SystemMessage(content=full_instruction),
        HumanMessage(content=input_text)
    ]
    
    try:
        response = model.invoke(messages)
        st.info(response.content)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

with st.form("my_form"):
    text = st.text_area("Tanyakan seputar Poltesa:")
    submitted = st.form_submit_button("Tanya")
    
    if submitted:
        generate_response(text)

