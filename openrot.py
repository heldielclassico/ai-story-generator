import streamlit as st
import os
from dotenv import load_dotenv
# Ganti import ini
from langchain_openai import ChatOpenAI 

# ... (bagian load_dotenv dan fungsi lainnya tetap sama) ...

def generate_response(user_input):
    # Ambil API Key OpenRouter dari .env
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_api_key:
        st.error("API Key OpenRouter tidak ditemukan!")
        return

    instruction = load_system_prompt("prompt.txt")
    
    # --- KONFIGURASI OPENROUTER ---
    model = ChatOpenAI(
        model="google/gemini-2.5-flash-lite-001", # Sesuaikan dengan ID model di OpenRouter
        openai_api_key=openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0,
        # Header tambahan opsional untuk OpenRouter
        default_headers={
            "HTTP-Referer": "http://localhost:8501", # Ganti dengan domain Anda jika sudah deploy
            "X-Title": "Asisten Poltesa"
        }
    )
    
    # --- PROMPT (Tetap sama) ---
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
    2. Jika pertanyaan pengguna tidak dapat dijawab menggunakan DATA REFERENSI, jawablah: "Maaf, informasi tersebut saat ini tidak tersedia dalam database resmi kami."
    3. DILARANG memberikan jawaban berdasarkan pengetahuan umum atau data di luar teks di atas.
    4. Jawablah secara langsung, singkat, dan profesional.

    PERTANYAAN PENGGUNA: 
    {user_input}

    JAWABAN:
    """
    
    try:
        response = model.invoke(final_prompt)
        if response and response.content:
            st.info(response.content)
        else:
            st.warning("AI tidak dapat merumuskan jawaban.")
    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")

# ... (bagian UI tetap sama) ...