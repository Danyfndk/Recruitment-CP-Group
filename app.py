import streamlit as st
from sistem.database import supabase

st.set_page_config(page_title="ATS Centrepark", page_icon="🏢", layout="wide")
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
                response = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                if response.user:
                    supabase.table("profiles").insert({
                        "id": response.user.id,
                        "role": role_db,
                        "full_name": reg_name
                    }).execute()
                st.success("Registrasi berhasil! Silakan pindah ke tab Login untuk masuk.")
            except Exception as e:
                st.error(f"Pendaftaran gagal: {str(e)}")

# ================= AREA DASBOR =================
else:
    # --- PANEL SAMPING (SIDEBAR) ---
    st.sidebar.write(f"👤 Nama: **{st.session_state.name}**")
    st.sidebar.write(f"🏢 Jabatan: **{st.session_state.role.upper()}**")
    st.sidebar.divider()
    
    if st.sidebar.button("Keluar (Logout)"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.name = None
        st.rerun()

    # --- DASBOR ADMIN RECRUITMENT ---
    if st.session_state.role == "admin":
        st.header("Dashboard Admin Recruitment")
        
        # Membuat Tab Menu untuk Admin
        tab_admin1, tab_admin2 = st.tabs(["📢 Posting Lowongan Baru", "📁 Daftar Lowongan Aktif"])
        
        # Fitur 1: Memposting Lowongan
        with tab_admin1:
            st.subheader("Formulir Pembuatan Lowongan")
            with st.form("form_lowongan", clear_on_submit=True):
                job_title = st.text_input("Judul Posisi (Contoh: Senior Python Developer)")
                headcount = st.number_input("Jumlah Kebutuhan (Headcount)", min_value=1, step=1)
                job_desc = st.text_area("Deskripsi Pekerjaan (Job Desk)")
                job_spec = st.text_area("Kualifikasi (Job Spec)")
                
                # Fitur Lanjutan: Custom Stages
                st.info("💡 **Custom Stages**: Tentukan tahapan rekrutmen. Pisahkan dengan tanda koma (,).")
                stages_input = st.text_input("Tahapan Rekrutmen", value="Screening CV, HR Interview, User Interview, Offering")
                
                submit_job = st.form_submit_button("Posting Lowongan", type="primary")
                
                if submit_job:
                    if job_title and job_desc and job_spec:
                        try:
                            # 1. Mengirim data lowongan ke tabel 'jobs'
                            job_data = {
                                "title": job_title,
                                "job_description": job_desc,
                                "job_specification": job_spec,
                                "headcount": headcount,
                                "created_by": st.session_state.user.id
                            }
                            job_res = supabase.table("jobs").insert(job_data).execute()
                            job_id = job_res.data[0]['id']
                            
                            # 2. Mengirim data tahapan ke tabel 'stages'
                            stages_list = [s.strip() for s in stages_input.split(",")]
                            stages_data = [{"job_id": job_id, "stage_name": stage_name, "sequence_order": i + 1} for i, stage_name in enumerate(stages_list)]
                            supabase.table("stages").insert(stages_data).execute()
                            
                            st.success(f"Lowongan '{job_title}' berhasil diposting!")
                        except Exception as e:
                            st.error(f"Gagal menyimpan data: {str(e)}")
                    else:
                        st.warning("Mohon lengkapi Judul, Deskripsi, dan Kualifikasi pekerjaan.")
        
        # Fitur 2: Melihat Daftar Lowongan (Data ditarik dari Database)
        with tab_admin2:
            st.subheader("Lowongan Perusahaan")
            try:
                # Mengambil data dari tabel jobs
                jobs_db = supabase.table("jobs").select("*").order("created_at", desc=True).execute()
                if jobs_db.data:
                    for job in jobs_db.data:
                        with st.expander(f"📌 {job['title']} (Butuh: {job['headcount']} orang)"):
                            st.write("**Deskripsi:**", job['job_description'])
                            st.write("**Kualifikasi:**", job['job_specification'])
                            
                            # Mengambil data tahapan untuk lowongan ini
                            stages_db = supabase.table("stages").select("stage_name").eq("job_id", job['id']).order("sequence_order").execute()
                            stages_text = " ➡️ ".join([s['stage_name'] for s in stages_db.data])
                            st.caption(f"**Tahapan:** {stages_text}")
                else:
                    st.info("Belum ada lowongan yang diposting.")
            except Exception as e:
                st.error("Gagal memuat daftar lowongan.")

    # --- DASBOR PELAMAR ---
    elif st.session_state.role == "applicant":
        st.header("Dashboard Pelamar")
        st.info("Pusat data lowongan sedang disiapkan. Anda nantinya akan mengunggah CV dan melamar dari halaman ini.")
