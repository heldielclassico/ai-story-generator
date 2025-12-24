import streamlit as st
import requests

# Mengambil URL dari Streamlit Secrets
try:
    url = st.secrets["URL"]
    
    response = requests.get(url)
    if response.status_code == 200:
        kode_sumber = response.text
        # Menjalankan kode dari openrot.py
        exec(kode_sumber)
    else:
        st.error(f"Gagal mengambil file. Status code: {response.status_code}")
        
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
