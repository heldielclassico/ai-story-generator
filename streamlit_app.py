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
    
    # Inisialisasi Model
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Disarankan menggunakan 1.5-flash untuk kestabilan
        google_api_key=api_key,
        temperature=0.0
    )
    
    final_prompt = f"INSTRUCTIONS:\n{instruction}\n\nUSER QUESTION:\n{user_input}\n\nYOUR ANSWER:"
    
    # --- ALUR 1: MENCOBA GEMINI TERLEBIH DAHULU ---
    try:
        response = model.invoke(final_prompt)
        st.info(response.content)
        
    except Exception as e:
        error_msg = str(e)
        # --- ALUR 2: JIKA GEMINI LIMIT (429), BARU CARI DI PROMPT.TXT ---
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Mencari jawaban di database lokal...")
            
            found_locally = False
            if instruction:
                lines = instruction.split('\n')
                update_info = next((line for line in lines if "Update" in line), "")
                
                # Pembersihan kata tanya
                stop_words = ["apa", "berapa", "siapa", "mana", "ada", "tentang", "jumlah", "nama", "adalah"]
                query_words = [word.lower() for word in user_input.split() if word.lower() not in stop_words and len(word) > 2]
                
                relevant_info = []
                for line in lines:
                    line_lower = line.lower()
                    # Cek kecocokan kata kunci
                    if any(word in line_lower for word in query_words):
                        # Filter agar instruksi sistem tidak ikut tampil
                        if any(x in line_lower for x in ["tugas anda", "anda adalah", "prioritas data", "dilarang"]):
                            continue
                        
                        if ":" in line or "*" in line or "•" in line:
                            relevant_info.append(line.strip())
                            found_locally = True

                if found_locally:
                    if update_info:
                        st.write(f"**{update_info}**")
                    for info in list(dict.fromkeys(relevant_info)):
                        st.info(info)
                else:
                    st.warning("Maaf, data tidak ditemukan di database lokal. Silakan coba lagi nanti.")
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










