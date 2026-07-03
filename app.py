import streamlit as st
from sistem.database import supabase

st.set_page_config(page_title="ATS Centrepark", page_icon="🏢")
st.title("Sistem Rekrutmen PT Centrepark Citra Corpora")

if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.name = None

# ================= AREA PENGUNJUNG =================
if st.session_state.user is None:
    st.write("Silakan Login atau Daftar akun baru untuk melanjutkan.")
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Registrasi Akun"])
    
    with tab1:
        log_email = st.text_input("Email", key="log_email")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        if st.button("Masuk (Login)", type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": log_email, "password": log_pass})
                st.session_state.user = response.user
                
                profile = supabase.table("profiles").select("role, full_name").eq("id", response.user.id).execute()
                if profile.data:
                    st.session_state.role = profile.data[0]['role']
                    st.session_state.name = profile.data[0]['full_name']
                    
                st.success("Login berhasil! Memuat dasbor...")
                st.rerun()
            except Exception as e:
                st.error("Login gagal. Pastikan Email dan Password Anda benar.")

    with tab2:
        reg_name = st.text_input("Nama Lengkap")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Mendaftar Sebagai:", ["Pelamar", "Admin Recruitment"])
        
        role_db = "applicant" if reg_role == "Pelamar" else "admin"
        
        if st.button("Daftar Sekarang"):
            try:
                # 1. Daftarkan akun utama ke sistem keamanan
                response = supabase.auth.sign_up({
                    "email": reg_email,
                    "password": reg_pass
                })
                
                # 2. Jika berhasil, masukkan data profilnya secara langsung ke tabel (By-pass trigger)
                if response.user:
                    supabase.table("profiles").insert({
                        "id": response.user.id,
                        "role": role_db,
                        "full_name": reg_name
                    }).execute()
                    
                st.success("Registrasi berhasil! Silakan pindah ke tab Login untuk masuk.")
            except Exception as e:
                # Jika muncul "User already registered", itu artinya akun sudah tersangkut 
                # dari percobaan sebelumnya, gunakan email fiktif lain untuk tes.
                st.error(f"Pendaftaran gagal: {str(e)}")

# ================= AREA DASBOR =================
else:
    st.sidebar.write(f"👤 Nama: **{st.session_state.name}**")
    st.sidebar.write(f"🏢 Jabatan: **{st.session_state.role.upper()}**")
    st.sidebar.divider()
    
    if st.sidebar.button("Keluar (Logout)"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.name = None
        st.rerun()

    if st.session_state.role == "admin":
        st.header("Dashboard Admin Recruitment")
        st.info("Selamat datang. Di sinilah Anda nantinya dapat memposting lowongan, mengatur tahapan tes, dan melihat ringkasan pelamar.")
        
    elif st.session_state.role == "applicant":
        st.header("Dashboard Pelamar")
        st.info("Selamat datang. Di sinilah Anda nantinya akan mengunggah CV, melamar posisi, dan melihat status lamaran.")
