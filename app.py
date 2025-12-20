import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Load environment variables (untuk lokal)
load_dotenv()

# Konfigurasi Halaman
st.set_page_config(page_title="AI Story Generator", page_icon="📖", layout="centered")

# Judul Aplikasi
st.title("📖 Generator Cerita Sederhana")
st.markdown("Masukkan topik dan biarkan AI merangkai cerita untukmu.")

# 2. Ambil API key (dari .env lokal atau Secrets online)
google_api_key = os.getenv("GOOGLE_API_KEY")

if google_api_key:
    os.environ['GOOGLE_API_KEY'] = google_api_key

    # Inisialisasi Model & Chain (Gemini 1.5 Flash adalah versi paling stabil)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    template_text = "Buat cerita menarik tentang {topik}. Gunakan gaya bahasa yang kreatif dan mudah dipahami dalam Bahasa Indonesia."
    prompt = PromptTemplate.from_template(template_text)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Fungsi untuk Reset/Clear
    def clear_text():
        st.session_state["input_topik"] = ""
        if "hasil_cerita" in st.session_state:
            del st.session_state["hasil_cerita"]

    # 3. Input Pengguna (Resizable Text Area)
    topik = st.text_area(
        "Masukkan topik cerita:", 
        placeholder="Contoh: Petualangan kucing di ruang angkasa...",
        height=150,
        key="input_topik"
    )

    # Baris tombol utama
    col_buat, col_reset = st.columns([4, 1])
    
    with col_buat:
        btn_buat = st.button("🚀 Buat Cerita", type="primary", use_container_width=True)
    
    with col_reset:
        st.button("🗑️ Clear", on_click=clear_text, use_container_width=True)

    if btn_buat:
        if topik:
            with st.spinner("Sedang menulis cerita..."):
                try:
                    hasil = chain.invoke({"topik": topik})
                    st.session_state.hasil_cerita = hasil
                    st.session_state.current_topic = topik[:20] 
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Tuliskan topik terlebih dahulu!")

    st.divider()

    # 4. Menampilkan Hasil dengan Tombol Sejajar (Versi Cloud Friendly)
    if "hasil_cerita" in st.session_state:
        cerita = st.session_state.hasil_cerita
        topik_save = st.session_state.get("current_topic", "cerita")

        # Layout Baris Hasil
        col_judul, col_copy, col_dl = st.columns([2, 0.5, 0.5])

        with col_judul:
            st.subheader("Hasil Cerita")
        
        with col_copy:
            # Fitur Copy menggunakan JavaScript agar tidak error di Cloud
            if st.button("📋 Copy", use_container_width=True):
                # Menjalankan script di browser pengguna
                js_code = f"navigator.clipboard.writeText(`{cerita}`)"
                st.components.v1.html(f"<script>{js_code}</script>", height=0)
                st.toast("Tersalin ke Clipboard!", icon="✅")

        with col_dl:
            st.download_button(
                label="📥 Save",
                data=cerita,
                file_name=f"cerita_{topik_save.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        # Area Teks Hasil Cerita (Resizable)
        st.text_area("", cerita, height=400, label_visibility="collapsed")

else:
    st.error("Google API Key tidak ditemukan. Jika sudah online, masukkan API Key di 'Settings > Secrets' di dashboard Streamlit.")

# Footer
st.caption("Dibuat dengan Streamlit & LangChain")
