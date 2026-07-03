import streamlit as st
import pandas as pd
from sistem.database import supabase

st.set_page_config(page_title="ATS Centrepark", page_icon="🏢", layout="wide")
st.title("Sistem Rekrutmen PT Centrepark Citra Corpora")

# Inisialisasi Session State
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.name = None

def muat_profil():
    if st.session_state.user:
        try:
            profil = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).execute()
            if profil.data:
                st.session_state.role = profil.data[0]['role']
                st.session_state.name = profil.data[0]['full_name']
            else:
                st.session_state.role = None
                st.session_state.name = None
        except Exception:
            pass

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
                muat_profil()
                st.success("Login berhasil! Memuat dasbor...")
                st.rerun()
            except Exception as e:
                st.error("Login gagal. Pastikan Email dan Password benar.")

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
                    try:
                        supabase.table("profiles").insert({
                            "id": response.user.id, "role": role_db, "full_name": reg_name
                        }).execute()
                    except Exception:
                        pass # Dibiarkan agar ditangani oleh fitur perbaikan mandiri di bawah
                st.success("Registrasi berhasil! Silakan Login.")
            except Exception as e:
                st.error(f"Pendaftaran gagal: {str(e)}")

# ================= AREA PERBAIKAN PROFIL =================
elif st.session_state.user and st.session_state.role is None:
    st.warning("⚠️ Sistem mendeteksi profil Anda belum tersimpan. Silakan lengkapi data Anda untuk masuk.")
    with st.form("form_perbaikan_profil"):
        nama_baru = st.text_input("Nama Lengkap")
        peran_baru = st.selectbox("Pilih Peran", ["Admin Recruitment", "Pelamar"])
        role_baru = "admin" if peran_baru == "Admin Recruitment" else "applicant"
        
        if st.form_submit_button("Simpan Profil & Masuk", type="primary"):
            if nama_baru:
                try:
                    # Menggunakan metode Insert yang jauh lebih aman untuk database baru
                    supabase.table("profiles").insert({
                        "id": st.session_state.user.id, 
                        "role": role_baru, 
                        "full_name": nama_baru
                    }).execute()
                    
                    muat_profil()
                    st.rerun()
                except Exception as e:
                    # Menangkap error murni dari Database agar aplikasi tidak crash
                    st.error(f"Gagal menyimpan ke Database (Kode Error: {str(e)})")
            else:
                st.error("Nama wajib diisi.")

# ================= AREA DASBOR ADMIN =================
elif st.session_state.user and st.session_state.role == "admin":
    st.sidebar.write(f"👤 **{st.session_state.name}**")
    st.sidebar.write(f"🏢 **ADMIN RECRUITMENT**")
    st.sidebar.divider()
    if st.sidebar.button("Keluar (Logout)"):
        supabase.auth.sign_out()
        st.session_state.user = None; st.session_state.role = None; st.session_state.name = None
        st.rerun()

    st.header("Dashboard Admin Recruitment")
    
    # 5 Tab Fitur Utama Admin sesuai cetak biru Anda
    tab_prof, tab_post, tab_track, tab_cv, tab_talent = st.tabs([
        "👤 Profil Saya", "📢 Posting Lowongan", "👥 Tracking Pelamar", "🤖 CV Matching", "🔍 Talent Search"
    ])
    
    # 1. TAB PROFIL ADMIN
    with tab_prof:
        st.subheader("Data Diri Admin")
        try:
            admin_data = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).execute().data[0]
            with st.form("form_update_admin"):
                upd_name = st.text_input("Nama Lengkap", value=admin_data.get('full_name', ''))
                upd_phone = st.text_input("Nomor Telepon", value=admin_data.get('phone_number', '') or '')
                if st.form_submit_button("Perbarui Data"):
                    supabase.table("profiles").update({"full_name": upd_name, "phone_number": upd_phone}).eq("id", st.session_state.user.id).execute()
                    muat_profil()
                    st.success("Profil diperbarui!")
                    st.rerun()
        except Exception as e:
            st.error("Gagal memuat profil admin dari database.")

    # 2. TAB POSTING LOWONGAN & CUSTOM STAGES
    with tab_post:
        st.subheader("Buat Lowongan Pekerjaan Baru")
        with st.form("form_lowongan", clear_on_submit=True):
            job_title = st.text_input("Judul Posisi (Contoh: Senior Python Developer)")
            headcount = st.number_input("Jumlah Kebutuhan (Headcount)", min_value=1)
            job_desc = st.text_area("Deskripsi Pekerjaan (Job Desk)")
            job_spec = st.text_area("Kualifikasi (Job Spec)")
            st.info("💡 **Custom Stages**: Tentukan tahapan rekrutmen dipisah dengan koma (,)")
            stages_input = st.text_input("Tahapan Rekrutmen", value="Screening CV, HR Interview, User Interview, Offering")
            
            if st.form_submit_button("Posting Lowongan", type="primary"):
                if job_title and job_desc:
                    try:
                        job_res = supabase.table("jobs").insert({
                            "title": job_title, "job_description": job_desc, 
                            "job_specification": job_spec, "headcount": headcount, 
                            "created_by": st.session_state.user.id
                        }).execute()
                        
                        job_id = job_res.data[0]['id']
                        stages_list = [s.strip() for s in stages_input.split(",")]
                        stages_data = [{"job_id": job_id, "stage_name": s, "sequence_order": i+1} for i, s in enumerate(stages_list)]
                        supabase.table("stages").insert(stages_data).execute()
                        st.success(f"Lowongan '{job_title}' berhasil diposting!")
                    except Exception as e:
                        st.error(f"Gagal memposting lowongan: {e}")

    # 3. TAB TRACKING PELAMAR
    with tab_track:
        st.subheader("Manajemen Data Pelamar")
        try:
            jobs = supabase.table("jobs").select("id, title").execute().data
            if jobs:
                job_opts = {j['title']: j['id'] for j in jobs}
                selected_job_title = st.selectbox("Pilih Lowongan", list(job_opts.keys()))
                selected_job_id = job_opts[selected_job_title]
                
                stages = supabase.table("stages").select("id, stage_name, sequence_order").eq("job_id", selected_job_id).order("sequence_order").execute().data
                stage_dict = {s['id']: s['stage_name'] for s in stages}
                
                apps = supabase.table("applications").select("id, status, match_score, current_stage_id, profiles(full_name, phone_number, cv_url)").eq("job_id", selected_job_id).execute().data
                
                if apps:
                    df_apps = []
                    for a in apps:
                        df_apps.append({
                            "Nama Pelamar": a['profiles']['full_name'],
                            "No. HP": a['profiles']['phone_number'] or "-",
                            "Tahapan Saat Ini": stage_dict.get(a['current_stage_id'], "Belum Diproses"),
                            "Status": a['status'].upper(),
                            "Match Score": f"{a['match_score']}%" if a['match_score'] else "N/A",
                            "App_ID": a['id']
                        })
                    st.dataframe(pd.DataFrame(df_apps).drop(columns=['App_ID']), use_container_width=True)
                    
                    st.divider()
                    st.write("**Pindahkan Tahapan Pelamar**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        pelamar_pilih = st.selectbox("Pilih Pelamar", [(a['id'], a['profiles']['full_name']) for a in apps], format_func=lambda x: x[1])
                    with col2:
                        stage_pilih = st.selectbox("Pindahkan ke Tahap", [(s['id'], s['stage_name']) for s in stages], format_func=lambda x: x[1])
                    with col3:
                        st.write("")
                        st.write("")
                        if st.button("Update Tahapan", use_container_width=True):
                            supabase.table("applications").update({"current_stage_id": stage_pilih[0]}).eq("id", pelamar_pilih[0]).execute()
                            st.success("Tahapan pelamar berhasil diperbarui!")
                            st.rerun()
                else:
                    st.info("Belum ada pelamar di posisi ini.")
            else:
                st.warning("Belum ada lowongan yang dibuat.")
        except Exception as e:
            st.error("Menunggu data operasional lowongan.")

    # 4. TAB CV MATCHING (ALGORITMA/AI)
    with tab_cv:
        st.subheader("CV Matching (AI Powered)")
        st.write("Sistem mencocokkan Job Spec dengan ekstraksi teks Resume Pelamar.")
        try:
            if jobs:
                job_cv = st.selectbox("Pilih Lowongan untuk di-Match", list(job_opts.keys()), key="cv_job")
                if st.button("Jalankan Algoritma Matching", type="primary"):
                    with st.spinner("Memproses NLP pada dokumen CV pelamar..."):
                        st.success("Matching Selesai! (Ini adalah modul simulasi visual untuk tahap ini).")
                        st.dataframe(pd.DataFrame({
                            "Nama Pelamar": ["Contoh Pelamar A", "Contoh Pelamar B"],
                            "Kesesuaian Skill": ["89.5%", "76.2%"],
                            "Rekomendasi": ["Sangat Disarankan", "Dipertimbangkan"]
                        }), use_container_width=True)
        except Exception:
            pass

    # 5. TAB TALENT SEARCH
    with tab_talent:
        st.subheader("Talent Search")
        st.write("Cari database pelamar menggunakan kata kunci spesifik (Misal: Python, Excel, Bahasa Inggris).")
        search_query = st.text_input("Masukkan Kata Kunci", placeholder="Ketik keahlian atau nama...")
        if st.button("Cari Talent"):
            if search_query:
                try:
                    search_res = supabase.table("profiles").select("full_name, role, phone_number").eq("role", "applicant").ilike("resume_text", f"%{search_query}%").execute()
                    if search_res.data:
                        st.dataframe(pd.DataFrame(search_res.data))
                    else:
                        st.info(f"Tidak ditemukan pelamar dengan kata kunci '{search_query}'.")
                except Exception as e:
                    st.error(f"Gagal melakukan pencarian.")

# ================= AREA DASBOR PELAMAR =================
elif st.session_state.user and st.session_state.role == "applicant":
    st.header("Dashboard Pelamar")
    st.info("Dasbor Pelamar siap dibangun pada iterasi selanjutnya.")
