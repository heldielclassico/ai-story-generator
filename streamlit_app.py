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

    # Memuat database teks dari prompt.txt
    instruction = load_system_prompt("prompt.txt")
    
    # --- ALUR 1: PRIORITAS PENCARIAN DINAMIS DI PROMPT.TXT ---
    found_locally = False
    if instruction:
        lines = instruction.split('\n')
        # Mencari baris yang mengandung tanggal update data
        update_info = next((line for line in lines if "Update" in line), "")
        
        # Membersihkan input user menjadi kata kunci (tokenizing)
        # Menghapus kata tanya umum agar pencarian lebih akurat
        stop_words = ["apa", "berapa", "siapa", "dimana", "mana", "bagaimana", "adalah", "tentang", "jumlah", "ada", "kah"]
        query_words = [word.lower() for word in user_input.split() if word.lower() not in stop_words and len(word) > 2]
        
        relevant_info = []
        for line in lines:
            # Mencocokkan kata kunci user dengan setiap baris di prompt.txt
            if any(word in line.lower() for word in query_words):
                # Validasi: Pastikan baris mengandung data (ditandai dengan ':' atau '-')
                # dan bukan baris instruksi sistem/identitas AI
                if (":" in line or "-" in line) and "Anda adalah" not in line:
                    relevant_info.append(line.strip())
                    found_locally = True

        # Jika ditemukan hasil yang cocok di lokal, tampilkan dan BERHENTI (tidak panggil Gemini)
        if found_locally:
            if update_info:
                st.write(f"**{update_info}**")
            
            # Menggunakan list(set()) untuk menghindari duplikasi baris
            for info in list(set(relevant_info)):
                st.info(info)
            return 

    # --- ALUR 2: JIKA TIDAK DITEMUKAN DI LOKAL, BARU AKTIFKAN GEMINI ---
    # Ganti model ke "gemini-1.5-flash" (disarankan untuk kestabilan saat ini)
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite", 
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
        # Jika Gemini terkena limit (429)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Silakan coba beberapa menit lagi.")
            # Fallback terakhir: Menampilkan isi prompt.txt jika AI gagal total
            with st.expander("Klik untuk melihat database informasi manual"):
                st.write(instruction)
        else:
            st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")

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




