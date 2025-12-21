def get_sheet_data():
    all_combined_data = ""
    try:
        # 1. Ambil URL utama dari secrets (pastikan ini URL tab 'sheetData' yang berisi daftar nama tab)
        # Contoh di secrets: SHEET_CENTRAL_URL = "https://docs.google.com/spreadsheets/d/ID/export?format=csv&gid=123"
        central_url = st.secrets["SHEET_CENTRAL_URL"]
        df_list = pd.read_csv(central_url)
        
        # Ambil daftar nama tab dari kolom 'NamaTab'
        tab_names = df_list['NamaTab'].tolist()
        
        # 2. Ambil Base URL (ID Spreadsheet)
        # Kita ambil bagian ID-nya saja agar bisa ganti-ganti gid secara otomatis
        base_url = central_url.split('/export')[0]
        
        for tab in tab_names:
            # Gunakan parameter 'sheet' untuk memanggil nama tab secara spesifik
            # Catatan: pandas bisa membaca sheet langsung jika menggunakan format /pub?output=xlsx
            # Tapi untuk CSV, kita gunakan format export dengan parameter sheet name
            tab_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={tab.replace(' ', '%20')}"
            
            try:
                df = pd.read_csv(tab_url)
                all_combined_data += f"\n\n### DATA {tab.upper()} ###\n"
                all_combined_data += df.to_string(index=False)
            except:
                continue # Jika satu tab gagal, lanjut ke tab berikutnya
                
        return all_combined_data
    except Exception as e:
        return ""
