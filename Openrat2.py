# --- 0. FIX UNTUK SQLITE (WAJIB DI BARIS PALING ATAS) ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import os
import pandas as pd
import requests
import re
import time
import io
from pypdf import PdfReader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Asisten POLTESA", page_icon="🎓")
PERSIST_DIRECTORY = "./db_poltesa"

# CSS Kustom
st.markdown("""
    <style>
    .stTextArea textarea { border-radius: 10px; }
    .stTextInput input { border-radius: 10px; }
    .stButton button { border-radius: 20px; }
    .duration-info { font-size: 0.75rem; color: #9ea4a9; font-style: italic; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNGSI LOGIKA DATA (PDF & VECTOR) ---

def extract_text_from_pdf(url):
    """Mengunduh dan mengekstrak teks dari URL PDF"""
    try:
        # Tambahkan timeout agar tidak menggantung jika link mati
        response = requests.get(url, timeout=15)
        with io.BytesIO(response.content) as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
    except Exception as e:
        st.warning(f"Gagal membaca PDF di {url}: {e}")
        return ""

def update_vector_database():
    """Mengambil data dari Sheet + PDF dan menyimpannya ke Vector DB"""
    with st.spinner("Sedang memproses data Poltesa... (Langkah ini mungkin memakan waktu 1-2 menit)"):
        try:
            central_url = st.secrets["SHEET_CENTRAL_URL"]
            df_list = pd.read_csv(central_url)
            tab_names = df_list['NamaTab'].tolist()
            base_url = central_url.split('/export')[0]
            
            all_docs = []
            # Pemotong teks: Mengatur ukuran potongan agar informasi tidak terputus
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

            for tab in tab_names:
                tab_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={tab.replace(' ', '%20')}"
                try:
                    df = pd.read_csv(tab_url)
                    
                    # 1. Proses Data Tabel (Text)
                    table_text = f"DATA DARI TAB {tab}:\n" + df.to_string(index=False)
                    chunks = text_splitter.split_text(table_text)
                    for chunk in chunks:
                        all_docs.append(Document(page_content=chunk, metadata={"source": tab}))
                    
                    # 2. Proses PDF (Jika ada kolom 'Link_PDF')
                    if 'Link_PDF' in df.columns:
                        for pdf_url in df['Link_PDF'].dropna():
                            if "http" in str(pdf_url):
                                pdf_text = extract_text_from_pdf(pdf_url)
                                if pdf_text:
                                    pdf_chunks = text_splitter.split_text(pdf_text)
                                    for p_chunk in pdf_chunks:
                                        all_docs.append(Document(page_content=p_chunk, metadata={"source": f"Dokumen {pdf_url}"}))
                except:
                    continue

            if not all_docs:
                st.error("Tidak ada data yang ditemukan untuk diproses.")
                return

            # 3. Inisialisasi Embeddings & Simpan ke ChromaDB
            embeddings = OpenAIEmbeddings(
                openai_api_key=st.secrets["OPENROUTER_API_KEY"],
                openai_api_base="https://openrouter.ai/api/v1"
            )
            
            # Buat database baru dari dokumen yang dikumpulkan
            vector_db = Chroma.from_documents(
                documents=all_docs,
                embedding=embeddings,
                persist_directory=PERSIST_DIRECTORY
            )
            vector_db.persist()
            st.success(f"Sinkronisasi selesai! {len(all_docs)} potongan informasi tersimpan.")
            st.rerun() # Refresh aplikasi
        except Exception as e:
            st.error(f"Terjadi kesalahan fatal: {e}")

# --- 3. TAMPILAN SIDEBAR ---
with st.sidebar:
    st.title("🎓 Sivita Admin")
    st.info("Gunakan panel ini untuk memperbarui pengetahuan asisten.")
    if st.button("🔄 Sinkronkan Data (Sheet & PDF)"):
        update_vector_database()
    
    st.divider()
    st.caption("Sivita v1.5 - Poltesa @ 2026")

# --- 4. LOGIKA PENCARIAN & CHAT ---

def generate_response(user_input):
    start_time = time.time()
    try:
        # Cek apakah database sudah ada
        if not os.path.exists(PERSIST_DIRECTORY):
            st.error("Database kosong! Klik 'Sinkronkan Data' di sidebar terlebih dahulu.")
            return

        # 1. Load Vector DB
        embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENROUTER_API_KEY"])
        vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        
        # 2. Cari konteks yang paling relevan (Top 4)
        docs = vector_db.similarity_search(user_input, k=4)
        context_data = "\n\n".join([f"Sumber {d.metadata['source']}:\n{d.page_content}" for d in docs])
        
        # 3. Panggil AI Gemini
        model = ChatOpenAI(
            model="google/gemini-2.0-flash-lite-001",
            openai_api_key=st.secrets["OPENROUTER_API_KEY"],
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.2
        )
        
        instruction = st.secrets["SYSTEM_PROMPT"]
        final_prompt = f"{instruction}\n\nKONTEKS RESMI POLTESA:\n{context_data}\n\nPERTANYAAN USER: {user_input}"
        
        response = model.invoke(final_prompt)
        
        # Simpan ke session state
        st.session_state["last_answer"] = response.content
        st.session_state["last_duration"] = round(time.time() - start_time, 2)
        
    except Exception as e:
        st.error(f"Gagal menghasilkan jawaban: {e}")

# --- 5. TAMPILAN UTAMA ---
st.title("🎓 Asisten Virtual Poltesa (Sivita)")
st.markdown("<p style='margin-top: -20px; color: gray;'>Pengetahuan berbasis Data Resmi & Dokumen PDF</p>", unsafe_allow_html=True)

# Container Form
with st.container():
    with st.form("chat_form", clear_on_submit=False):
        user_email = st.text_input("Masukan Gmail Anda:", placeholder="contoh@gmail.com")
        user_text = st.text_area("Apa yang ingin Anda tanyakan?", placeholder="Tanyakan tentang pendaftaran, UKT, atau aturan kampus...")
        
        submitted = st.form_submit_button("Kirim Pertanyaan", use_container_width=True)
        
        if submitted:
            if not user_email or "@gmail.com" not in user_email:
                st.error("Harap gunakan format email @gmail.com yang valid.")
            elif not user_text.strip():
                st.warning("Pertanyaan tidak boleh kosong.")
            else:
                with st.spinner("Sivita sedang berpikir..."):
                    generate_response(user_text)

# Menampilkan Jawaban
if "last_answer" in st.session_state and st.session_state["last_answer"]:
    st.divider()
    st.chat_message("assistant").markdown(st.session_state["last_answer"])
    st.markdown(f'<p class="duration-info">⏱️ Selesai diproses dalam {st.session_state["last_duration"]} detik</p>', unsafe_allow_html=True)
