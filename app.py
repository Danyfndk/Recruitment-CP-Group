import streamlit as st
import pandas as pd
from sistem.database import supabase

# Konfigurasi Halaman (Harus selalu di baris pertama)
st.set_page_config(page_title="Centrepark Careers", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# ================= CUSTOM CSS (UI/UX SAAS LEVEL) =================
st.markdown("""
<style>
    /* Menyembunyikan elemen bawaan Streamlit agar terlihat seperti Web Mandiri */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modifikasi Jarak Atas */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Desain Tombol Profesional */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Desain Kartu (Card) untuk Konten */
    div[data-testid="stForm"], div.css-1r6slb0, div.css-12oz5g7 {
        border-radius: 12px;
        padding: 24px;
        background-color: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Judul Utama */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

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

# ================= AREA PENGUNJUNG (HALAMAN LOGIN SAAS) =================
if st.session_state.user is None:
    st.markdown('<p class="main-title">PT Centrepark Citra Corpora</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sistem Rekrutmen Terpadu & Akuisisi Talenta</p>', unsafe_allow_html=True)
    
    # Membuat Layout Tengah (Center Alignment)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔒 Masuk Sistem", "📝 Registrasi Kandidat"])
        
        with tab1:
            st.markdown("#### Selamat Datang Kembali")
            log_email = st.text_input("Alamat Email", placeholder="email@domain.com", key="log_email")
            log_pass = st.text_input("Kata Sandi", type="password", placeholder="••••••••", key="log_pass")
            st.write("") # Spacing
            if st.button("Masuk (Login)", type="primary", use_container_width=True):
                if log_email and log_pass:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": log_email, "password": log_pass})
                        st.session_state.user = response.user
                        muat_profil()
                        st.rerun()
                    except Exception as e:
                        st.error("Kredensial tidak valid. Silakan periksa kembali email dan kata sandi Anda.")
                else:
                    st.warning("Mohon lengkapi email dan kata sandi.")

        with tab2:
            st.markdown("#### Bergabung Bersama Kami")
            reg_name = st.text_input("Nama Lengkap Sesuai KTP")
            reg_email = st.text_input("Alamat Email", key="reg_email")
            reg_pass = st.text_input("Buat Kata Sandi", type="password", key="reg_pass")
            reg_role = st.selectbox("Mendaftar Sebagai", ["Pelamar", "Admin Recruitment"])
            role_db = "applicant" if reg_role == "Pelamar" else "admin"
            
            st.write("") # Spacing
            if st.button("Buat Akun Baru", use_container_width=True):
                if reg_name and reg_email and reg_pass:
                    try:
                        response = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                        if response.user:
                            try:
                                supabase.table("profiles").insert({"id": response.user.id, "role": role_db, "full_name": reg_name}).execute()
                            except: pass
                        st.success("Registrasi berhasil! Silakan masuk melalui tab Login.")
                    except Exception as e:
                        st.error("Gagal mendaftarkan akun. Email mungkin sudah digunakan.")
                else:
                    st.warning("Mohon lengkapi seluruh kolom formulir.")

# ================= AREA PERBAIKAN PROFIL (SELF-HEALING) =================
elif st.session_state.user and st.session_state.role is None:
    st.markdown('<p class="main-title">Penyelesaian Profil</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.warning("Sistem mendeteksi data diri Anda belum lengkap.")
        with st.form("form_perbaikan"):
            nama_baru = st.text_input("Nama Lengkap Valid")
            peran_baru = st.selectbox("Pilih Peran Akses", ["Admin Recruitment", "Pelamar"])
            role_baru = "admin" if peran_baru == "Admin Recruitment" else "applicant"
            
            if st.form_submit_button("Simpan & Lanjutkan", use_container_width=True):
                if nama_baru:
                    try:
                        supabase.table("profiles").insert({"id": st.session_state.user.id, "role": role_baru, "full_name": nama_baru}).execute()
                        muat_profil()
                        st.rerun()
                    except Exception as e:
                        st.error("Terjadi kendala pada server database.")

# ================= AREA DASBOR ADMIN RECRUITMENT =================
elif st.session_state.user and st.session_state.role == "admin":
    # --- PANEL SIDEBAR SAAS ---
    with st.sidebar:
        st.markdown(f"### 🏢 Workspace")
        st.caption("PT Centrepark Citra Corpora")
        st.divider()
        st.markdown(f"**👤 {st.session_state.name}**")
        st.caption("Administrator Rekrutmen")
        st.write("")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None; st.session_state.role = None; st.session_state.name = None
            st.rerun()

    st.markdown("## 📊 Dasbor Administrator")
    
    # --- KPI METRICS (Tampilan Data Eksekutif) ---
    try:
        total_jobs = len(supabase.table("jobs").select("id").execute().data)
        total_apps = len(supabase.table("applications").select("id").execute().data)
    except:
        total_jobs, total_apps = 0, 0
        
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lowongan Aktif", f"{total_jobs} Posisi")
    m2.metric("Total Pelamar", f"{total_apps} Orang")
    m3.metric("Kandidat Diproses", "0 Orang") # Dummy for visual
    m4.metric("Kandidat Diterima", "0 Orang") # Dummy for visual
    st.write("")

    # --- TAB MENU MODERN ---
    t_lowongan, t_kandidat, t_ai, t_talent, t_profil = st.tabs([
        "💼 Manajemen Lowongan", "👥 Tracking Kandidat", "🤖 AI CV Matching", "🔍 Pencarian Talenta", "⚙️ Pengaturan"
    ])
    
    # TAB 1: MANAJEMEN LOWONGAN
    with t_lowongan:
        col_list, col_form = st.columns([1.5, 1])
        
        with col_form:
            st.markdown("#### ➕ Buat Lowongan Baru")
            with st.form("form_lowongan", clear_on_submit=True):
                job_title = st.text_input("Judul Posisi (Wajib)")
                headcount = st.number_input("Kebutuhan Karyawan (Headcount)", min_value=1)
                job_desc = st.text_area("Deskripsi Pekerjaan")
                job_spec = st.text_area("Kualifikasi Khusus")
                stages_input = st.text_input("Tahapan (Gunakan koma)", value="Screening CV, HR Interview, User Interview, Offering")
                
                if st.form_submit_button("Publikasikan Lowongan", type="primary", use_container_width=True):
                    if job_title:
                        try:
                            job_res = supabase.table("jobs").insert({
                                "title": job_title, "job_description": job_desc, "job_specification": job_spec, 
                                "headcount": headcount, "created_by": st.session_state.user.id
                            }).execute()
                            job_id = job_res.data[0]['id']
                            stages_list = [s.strip() for s in stages_input.split(",")]
                            stages_data = [{"job_id": job_id, "stage_name": s, "sequence_order": i+1} for i, s in enumerate(stages_list)]
                            supabase.table("stages").insert(stages_data).execute()
                            st.success(f"Lowongan '{job_title}' mengudara!")
                            st.rerun()
                        except Exception as e: st.error("Gagal menyimpan data.")
                    else: st.warning("Judul posisi wajib diisi.")
                    
        with col_list:
            st.markdown("#### 📋 Daftar Lowongan Perusahaan")
            try:
                jobs_db = supabase.table("jobs").select("*").order("created_at", desc=True).execute().data
                if jobs_db:
                    for job in jobs_db:
                        with st.expander(f"📌 {job['title']} — Kebutuhan: {job['headcount']} orang"):
                            st.write("**Deskripsi:**", job['job_description'] or "-")
                            st.write("**Kualifikasi:**", job['job_specification'] or "-")
                            stages_db = supabase.table("stages").select("stage_name").eq("job_id", job['id']).order("sequence_order").execute().data
                            st.caption(f"**Alur:** {' ➡️ '.join([s['stage_name'] for s in stages_db])}")
                else:
                    st.info("Belum ada lowongan yang dibuat.")
            except: st.error("Gagal memuat database.")

    # TAB 2: TRACKING KANDIDAT
    with t_kandidat:
        st.markdown("#### 📈 Papan Tracking Kandidat")
        try:
            jobs = supabase.table("jobs").select("id, title").execute().data
            if jobs:
                job_opts = {j['title']: j['id'] for j in jobs}
                selected_job_title = st.selectbox("Filter berdasarkan Lowongan", list(job_opts.keys()))
                selected_job_id = job_opts[selected_job_title]
                
                stages = supabase.table("stages").select("id, stage_name").eq("job_id", selected_job_id).order("sequence_order").execute().data
                stage_dict = {s['id']: s['stage_name'] for s in stages}
                
                apps = supabase.table("applications").select("id, status, match_score, current_stage_id, profiles(full_name, phone_number)").eq("job_id", selected_job_id).execute().data
                
                if apps:
                    df_apps = [{"Nama": a['profiles']['full_name'], "Kontak": a['profiles']['phone_number'] or "-", "Posisi Tahap": stage_dict.get(a['current_stage_id'], "-"), "Skor": f"{a['match_score']}%" if a['match_score'] else "N/A", "ID": a['id']} for a in apps]
                    st.dataframe(pd.DataFrame(df_apps).drop(columns=['ID']), use_container_width=True)
                    
                    st.markdown("##### ⚙️ Update Tahapan Kandidat")
                    c1, c2, c3 = st.columns(3)
                    with c1: p_pelamar = st.selectbox("Pilih Kandidat", [(a['id'], a['profiles']['full_name']) for a in apps], format_func=lambda x: x[1])
                    with c2: p_tahap = st.selectbox("Pindah ke Tahap", [(s['id'], s['stage_name']) for s in stages], format_func=lambda x: x[1])
                    with c3:
                        st.write("")
                        if st.button("Simpan Perubahan", use_container_width=True):
                            supabase.table("applications").update({"current_stage_id": p_tahap[0]}).eq("id", p_pelamar[0]).execute()
                            st.success("Tahap diperbarui!"); st.rerun()
                else: st.info("Belum ada pelamar di posisi ini.")
            else: st.warning("Belum ada data lowongan.")
        except: st.error("Menunggu operasional sistem.")

    # TAB 3: AI CV MATCHING
    with t_ai:
        st.markdown("#### 🧠 Analisis CV & Spesifikasi Pekerjaan")
        st.write("Modul ini akan mengekstrak Resume pelamar dan memberikan skor kecocokan dengan *Job Specification*.")
        st.info("Status Sistem: Mesin NLP sedang disiapkan untuk iterasi berikutnya (Simulasi visual aktif).")

    # TAB 4: TALENT SEARCH
    with t_talent:
        st.markdown("#### 🔍 Direktori Pencarian Talenta")
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1: search_query = st.text_input("Kata Kunci (Keahlian, Tools, Nama)", label_visibility="collapsed", placeholder="Ketik kata kunci...")
        with col_s2: btn_search = st.button("Cari Database", type="primary", use_container_width=True)
        
        if btn_search and search_query:
            try:
                res = supabase.table("profiles").select("full_name, phone_number").eq("role", "applicant").ilike("resume_text", f"%{search_query}%").execute().data
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
                else: st.warning(f"Kandidat dengan kriteria '{search_query}' tidak ditemukan.")
            except: pass

    # TAB 5: PROFIL
    with t_profil:
        st.markdown("#### ⚙️ Pengaturan Profil Admin")
        admin_data = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).execute().data[0]
        c_prof1, c_prof2 = st.columns(2)
        with c_prof1:
            upd_name = st.text_input("Nama Lengkap", value=admin_data.get('full_name', ''))
            upd_phone = st.text_input("Nomor Telepon", value=admin_data.get('phone_number', '') or '')
            if st.button("Simpan Profil"):
                supabase.table("profiles").update({"full_name": upd_name, "phone_number": upd_phone}).eq("id", st.session_state.user.id).execute()
                muat_profil()
                st.success("Disimpan!"); st.rerun()

# ================= AREA DASBOR PELAMAR (PORTAL LOWONGAN) =================
elif st.session_state.user and st.session_state.role == "applicant":
    # --- PANEL SIDEBAR KANDIDAT ---
    with st.sidebar:
        st.markdown(f"### 👤 Portal Kandidat")
        st.divider()
        st.markdown(f"**{st.session_state.name}**")
        st.write("")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.user = None; st.session_state.role = None; st.session_state.name = None
            st.rerun()

    st.markdown("## 💼 Eksplorasi Karir")
    st.write("Temukan peluang karir terbaik di PT Centrepark Citra Corpora dan wujudkan potensi Anda bersama kami.")
    st.write("")
    
    try:
        # Mengambil lowongan yang aktif
        jobs_public = supabase.table("jobs").select("*").eq("is_open", True).order("created_at", desc=True).execute().data
        if jobs_public:
            # Membuat sistem Grid Layout untuk lowongan (2 Kolom)
            for i in range(0, len(jobs_public), 2):
                cols = st.columns(2)
                
                # Kartu Kiri
                with cols[0]:
                    job1 = jobs_public[i]
                    with st.container():
                        st.markdown(f"#### {job1['title']}")
                        st.caption(f"Kebutuhan: {job1['headcount']} Posisi | Tipe: Full-Time")
                        st.write(job1['job_description'][:150] + "..." if len(job1['job_description']) > 150 else job1['job_description'])
                        if st.button("Lihat Detail & Lamar", key=f"btn_{job1['id']}", use_container_width=True):
                            st.success("Fitur pengajuan lamaran dan Upload CV akan diaktifkan pada iterasi berikutnya.")
                            
                # Kartu Kanan (Jika Ada)
                if i + 1 < len(jobs_public):
                    with cols[1]:
                        job2 = jobs_public[i+1]
                        with st.container():
                            st.markdown(f"#### {job2['title']}")
                            st.caption(f"Kebutuhan: {job2['headcount']} Posisi | Tipe: Full-Time")
                            st.write(job2['job_description'][:150] + "..." if len(job2['job_description']) > 150 else job2['job_description'])
                            if st.button("Lihat Detail & Lamar", key=f"btn_{job2['id']}", use_container_width=True):
                                st.success("Fitur pengajuan lamaran dan Upload CV akan diaktifkan pada iterasi berikutnya.")
                st.write("") # Spacing antar baris
        else:
            st.info("Belum ada lowongan yang dibuka saat ini. Pantau terus portal kami.")
    except Exception as e:
        st.error("Gagal memuat portal karir.")
