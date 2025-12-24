import streamlit as st
import requests

# Link raw dari GitHub
url = "URL_RAW_GITHUB_OPENROT_PY_KAMU"

response = requests.get(url)
if response.status_code == 200:
    kode_sumber = response.text
    # Jalankan kodenya
    exec(kode_sumber)
else:
    st.error("Gagal mengambil file dari GitHub")
