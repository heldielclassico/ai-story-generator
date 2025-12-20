# 4. Fungsi Generate Response
def generate_response(user_input):
    if not api_key:
        st.error("API Key tidak ditemukan di file .env!")
        return

    instruction = load_system_prompt("prompt.txt")
    
    # --- PRIORITAS 1: PENCARIAN MANUAL DI PROMPT.TXT ---
    found_locally = False
    if instruction:
        lines = instruction.split('\n')
        update_info = next((line for line in lines if "Update" in line), "")
        
        # Mencari kata kunci penting dari input user (misal: "alumni", "mahasiswa", "prodi")
        keywords = ["alumni", "mahasiswa", "prodi", "dosen", "tendik", "penelitian", "kerjasama", "pkm"]
        user_query_lower = user_input.lower()
        
        relevant_info = []
        for line in lines:
            # Jika baris mengandung kata kunci yang ditanyakan user
            for key in keywords:
                if key in user_query_lower and key in line.lower():
                    relevant_info.append(line)
                    found_locally = True

        # Jika ditemukan di prompt.txt, tampilkan hasilnya
        if found_locally:
            if update_info:
                st.write(f"**{update_info}**")
            for info in relevant_info:
                st.info(info)
            return  # Berhenti di sini, tidak perlu panggil Gemini

    # --- PRIORITAS 2: JIKA TIDAK ADA DI PROMPT.TXT, BARU PAKAI GEMINI ---
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        google_api_key=api_key,
        temperature=0.0
    )
    
    final_prompt = f"INSTRUCTIONS:\n{instruction}\n\nUSER QUESTION:\n{user_input}\n\nYOUR ANSWER:"
    
    try:
        response = model.invoke(final_prompt)
        st.info(response.content)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            st.error("Kami sedang mengalami Gangguan Teknis. Silakan coba beberapa menit lagi.")
        else:
            st.error(f"Terjadi kesalahan: {e}")
