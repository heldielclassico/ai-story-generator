import requests
from bs4 import BeautifulSoup

def get_data_kerjasama():
    url = "https://poltesa.ac.id/kerjasama/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Selector 'td' biasanya digunakan jika data dalam bentuk tabel
            # Jika menggunakan class 'instansi', pastikan class tersebut ada di HTML
            instansi_elements = soup.find_all('div', class_='instansi') 
            
            if not instansi_elements:
                return "Data kerjasama tidak ditemukan di halaman web."
                
            daftar = [f"{i+1}. {el.get_text(strip=True)}" for i, el in enumerate(instansi_elements)]
            return "\n".join(daftar)
        return "Gagal mengakses data kerjasama (Status Error)."
    except Exception as e:
        return f"Error saat mengambil data: {str(e)}"