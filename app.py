import streamlit as st
from sistem.database import supabase

# Mengatur tampilan halaman
st.set_page_config(page_title="ATS Centrepark", page_icon="🏢")
st.title("Sistem Rekrutmen PT Centrepark Citra Corpora")

# Sistem Ingatan (Session State) untuk mengenali siapa yang sedang login
if 'user' not in st.session_state:
    st.session_state.user = None

# JIKA PENGGUNA BELUM LOGIN (Tampilkan Pintu Masuk)
if st.session_state.user is None:
    st.write("Silakan Login atau Daftar akun baru untuk melanjutkan.")
    
    # Membuat dua tab: Login dan Registrasi
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Registrasi Akun"])
    
    # --- BAGIAN LOGIN ---
    with tab1:
        log_email = st.text_input("Email", key="log_email")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        if st.button("Masuk (Login)", type="primary"):
            try:
                # Mengirim data login ke mesin Supabase
                response = supabase.auth.sign_in_with_password({"email": log_email, "password": log_pass})
                st.session_state.user = response.user
                st.success("Login berhasil! Memuat dasbor...")
                st.rerun() # Menyegarkan halaman
            except Exception as e:
                st.error("Login gagal. Pastikan Email dan Password Anda benar.")

    # --- BAGIAN REGISTRASI ---
    with tab2:
        reg_name = st.text_input("Nama Lengkap")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Mendaftar Sebagai:", ["Pelamar", "Admin Recruitment"])
        
        # Menerjemahkan pilihan bahasa Indonesia ke bahasa database
        role_db = "applicant" if reg_role == "Pelamar" else "admin"
        
        if st.button("Daftar Sekarang"):
            try:
                # Mengirim data pendaftaran ke Supabase
                response = supabase.auth.sign_up({
                    "email": reg_email,
                    "password": reg_pass,
                    "options": {"data": {"full_name": reg_name, "role": role_db}}
                })
                st.success("Registrasi berhasil! Silakan pindah ke tab Login untuk masuk.")
            except Exception as e:
                st.error(f"Pendaftaran gagal: {str(e)}")

# JIKA PENGGUNA SUDAH LOGIN (Tampilkan Dasbor)
else:
    st.success("Anda berhasil masuk ke dalam sistem!")
    st.write("Ini adalah area Dasbor (Fitur akan ditambahkan di tahap selanjutnya).")
    
    if st.button("Keluar (Logout)"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
