import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
st.title("🎓 Asisten Virtual Poltesa")

# --- FUNGSI: CLEAR INPUT ---
def clear_text():
    st.session_state["user_input"] = ""

# 2. Fungsi Generate Response (Menggunakan st.secrets)
def generate_response(user_input):
    # Mengambil API Key dan Prompt dari Streamlit Secrets secara aman
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        instruction = st.secrets["SYSTEM_PROMPT"]
    except KeyError:
        st.error("Konfigurasi Secrets (API Key atau Prompt) tidak ditemukan!")
        return

    # Inisialisasi Model Gemini 1.5 Flash
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    # Teknik Grounding Ketat (Prompt Rahasia)
    final_prompt = f"""
    SISTEM: 
    {instruction}

    PERTANYAAN PENGGUNA: 
    {user_input}

    JAWABAN:
    """
    
    try:
        # Menghubungi Gemini
        response = model.invoke(final_prompt)
        
        if response and response.content:
            st.info(response.content)
        else:
            st.warning("Sivita tidak dapat merumuskan jawaban berdasarkan data yang tersedia.")
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis (Limit Tercapai). Silakan coba beberapa menit lagi atau akses: www.poltesa.ac.id")
        else:
            st.error(f"Terjadi kesalahan teknis: {e}")

# 3. UI Form
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
            with st.spinner("Sivita sedang mencari data resmi..."):
                generate_response(user_text)

# Footer
st.markdown("---")
st.caption("Sivita - Asisten Virtual Resmi Politeknik Negeri Sambas (Update: 15 Desember 2025)")

