import streamlit as st
import pandas as pd
from sistem.database import supabase

st.set_page_config(page_title="Centrepark Careers", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")

# ================= CUSTOM CSS (UI/UX SAAS LEVEL) =================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stButton>button { border-radius: 8px; font-weight: 600; padding: 0.5rem 1rem; transition: all 0.3s ease; border: none; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    div[data-testid="stForm"], div.css-1r6slb0, div.css-12oz5g7 { border-radius: 12px; padding: 24px; background-color: rgba(128, 128, 128, 0.05); border: 1px solid rgba(128, 128, 128, 0.1); }
    .main-title { font-size: 2.5rem; font-weight: 800; text-align: center; background: -webkit-linear-gradient(45deg, #1E3A8A, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }
    .sub-title { text-align: center; color: #6B7280; font-size: 1.1rem; margin-bottom: 3rem; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None; st.session_state.role = None; st.session_state.name = None

def muat_profil():
    if st.session_state.user:
        try:
            profil = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).execute()
            if profil.data:
                st.session_state.role = profil.data[0]['role']
                st.session_state.name = profil.data[0]['full_name']
            else:
                st.session_state.role = None; st.session_state.name = None
        except Exception: pass

# ================= AREA PENGUNJUNG =================
if st.session_state.user is None:
    st.markdown('<p class="main-title">PT Centrepark Citra Corpora</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sistem Rekrutmen Terpadu & Akuisisi Talenta</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Masuk Sistem", "📝 Registrasi Kandidat"])
        
        with tab1:
            st.markdown("#### Selamat Datang Kembali")
            log_email = st.text_input("Alamat Email", placeholder="email@domain.com", key="log_email")
            log_pass = st.text_input("Kata Sandi", type="password", placeholder="••••••••", key="log_pass")
            st.write("")
            if st.button("Masuk (Login)", type="primary", use_container_width=True):
                if log_email and log_pass:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": log_email, "password": log_pass})
                        st.session_state.user = response.user
                        muat_profil()
                        st.rerun()
                    except Exception as e: st.error("Kredensial tidak valid. Silakan periksa kembali email dan kata sandi Anda.")
                else: st.warning("Mohon lengkapi email dan kata sandi.")

        with tab2:
            st.markdown("#### Bergabung Bersama Kami")
            reg_name = st.text_input("Nama Lengkap Sesuai KTP")
            reg_email = st.text_input("Alamat Email", key="reg_email")
            reg_pass = st.text_input("Buat Kata Sandi", type="password", key="reg_pass")
            reg_role = st.selectbox("Mendaftar Sebagai", ["Pelamar", "Admin Recruitment"])
            role_db = "applicant" if reg_role == "Pelamar" else "admin"
            st.write("")
            if st.button("Buat Akun Baru", use_container_width=True):
                if reg_name and reg_email and reg_pass:
                    try:
                        response = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                        if response.user:
                            try: supabase.table("profiles").insert({"id": response.user.id, "role": role_db, "full_name": reg_name}).execute()
                            except: pass
                        st.success("Registrasi berhasil! Silakan masuk melalui tab Login.")
                    except Exception as e: st.error("Gagal mendaftarkan akun. Email mungkin sudah digunakan.")
                else: st.warning("Mohon lengkapi seluruh kolom formulir.")

# ================= AREA PERBAIKAN PROFIL =================
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
                    except Exception as e: st.error("Terjadi kendala pada server database.")

# ================= AREA DASBOR ADMIN =================
elif st.session_state.user and st.session_state.role == "admin":
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
    try:
        total_jobs = len(supabase.table("jobs").select("id").execute().data)
        total_apps = len(supabase.table("applications").select("id").execute().data)
    except: total_jobs, total_apps = 0, 0
        
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lowongan Aktif", f"{total_jobs} Posisi")
    m2.metric("Total Pelamar", f"{total_apps} Orang")
    m3.metric("Kandidat Diproses", "0 Orang")
    m4.metric("Kandidat Diterima", "0 Orang")
    st.write("")

    t_lowongan, t_kandidat, t_ai, t_talent, t_profil = st.tabs(["💼 Manajemen Lowongan", "🗂️ Tracking Kandidat", "🤖 AI CV Matching", "🔍 Pencarian Talenta", "⚙️ Pengaturan"])
    
    with t_lowongan:
        col_list, col_form = st.columns([1.5, 1])
        with col_form:
            st.markdown("#### ➕ Buat Lowongan Baru")
            with st.form("form_lowongan", clear_on_submit=True):
                job_title = st.text_input("Judul Posisi (Wajib)")
                headcount = st.number_input("Kebutuhan Karyawan", min_value=1)
                job_desc = st.text_area("Deskripsi Pekerjaan")
                job_spec = st.text_area("Kualifikasi Khusus")
                
                # --- SISTEM BARU: MULTISELECT TERSTANDARISASI ---
                st.info("💡 **Tahapan Rekrutmen**: Urutan tahapan otomatis tercatat berdasarkan urutan klik Anda.")
                template_tahapan = [
                    "Screening CV", 
                    "Psikotes", 
                    "Skill Test", 
                    "Focus Group Discussion (FGD)", 
                    "HR Interview", 
                    "User Interview", 
                    "Direksi Interview",
                    "Medical Check Up (MCU)", 
                    "Offering"
                ]
                stages_list = st.multiselect(
                    "Pilih Komposisi Tahapan", 
                    options=template_tahapan,
                    default=["Screening CV", "Psikotes", "HR Interview", "User Interview", "Offering"]
                )
                
                if st.form_submit_button("Publikasikan Lowongan", type="primary", use_container_width=True):
                    if job_title and len(stages_list) > 0:
                        try:
                            job_res = supabase.table("jobs").insert({"title": job_title, "job_description": job_desc, "job_specification": job_spec, "headcount": headcount, "created_by": st.session_state.user.id}).execute()
                            job_id = job_res.data[0]['id']
                            
                            # Menggunakan stages_list langsung dari array multiselect tanpa split koma
                            stages_data = [{"job_id": job_id, "stage_name": s, "sequence_order": i+1} for i, s in enumerate(stages_list)]
                            supabase.table("stages").insert(stages_data).execute()
                            st.success("Berhasil!"); st.rerun()
                        except Exception as e: st.error("Gagal menyimpan data.")
                    else:
                        st.warning("Judul posisi dan minimal satu tahapan rekrutmen wajib diisi.")
                        
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
                else: st.info("Belum ada lowongan yang dibuat.")
            except: pass

    with t_kandidat:
        st.markdown("#### 🗂️ Sistem Papan Bucket Pelamar")
        st.write("Pantau dan pindahkan pelamar antar tahapan (bucket) secara aktual untuk mempermudah proses screening.")
        try:
            jobs = supabase.table("jobs").select("id, title").execute().data
            if jobs:
                job_opts = {j['title']: j['id'] for j in jobs}
                selected_job_title = st.selectbox("Pilih Papan Lowongan", list(job_opts.keys()))
                selected_job_id = job_opts[selected_job_title]
                
                stages = supabase.table("stages").select("id, stage_name, sequence_order").eq("job_id", selected_job_id).order("sequence_order").execute().data
                stage_dict = {s['id']: s['stage_name'] for s in stages}
                
                apps = supabase.table("applications").select("id, status, match_score, current_stage_id, profiles(full_name, phone_number, cv_url)").eq("job_id", selected_job_id).execute().data
                
                if stages:
                    st.divider()
                    kanban_cols = st.columns(len(stages))
                    for idx, stage in enumerate(stages):
                        with kanban_cols[idx]:
                            st.markdown(f"<div style='text-align:center; padding:10px; background-color:rgba(59, 130, 246, 0.05); border: 2px solid #3B82F6; border-radius:8px; margin-bottom: 15px;'><b>{stage['stage_name']}</b></div>", unsafe_allow_html=True)
                            stage_apps = [a for a in apps if a['current_stage_id'] == stage['id']]
                            if not stage_apps:
                                st.caption("Belum ada kandidat")
                            else:
                                for a in stage_apps:
                                    with st.container(border=True):
                                        st.markdown(f"**{a['profiles']['full_name']}**")
                                        if a['profiles']['cv_url']:
                                            st.markdown(f"[📄 Buka Berkas CV]({a['profiles']['cv_url']})")
                                        else:
                                            st.caption("Tanpa Dokumen CV")
                    st.divider()
                    if apps:
                        st.markdown("##### ⚙️ Screening & Pemindahan Bucket")
                        c1, c2, c3 = st.columns(3)
                        with c1: 
                            p_pelamar = st.selectbox("Pilih Kandidat", [(a['id'], a['profiles']['full_name'], a['current_stage_id']) for a in apps], format_func=lambda x: f"{x[1]} (Di Bucket: {stage_dict.get(x[2], '-')})")
                        with c2: 
                            p_tahap = st.selectbox("Pindahkan ke Bucket", [(s['id'], s['stage_name']) for s in stages], format_func=lambda x: x[1])
                        with c3:
                            st.write("")
                            if st.button("Pindahkan Kandidat", use_container_width=True, type="primary"):
                                supabase.table("applications").update({"current_stage_id": p_tahap[0]}).eq("id", p_pelamar[0]).execute()
                                st.success(f"Kandidat berhasil dipindahkan ke {p_tahap[1]}!")
                                st.rerun()
                    else:
                        st.info("Belum ada pelamar yang mendaftar di lowongan ini.")
                else:
                    st.warning("Lowongan ini tidak memiliki tahapan. Silakan periksa kembali data lowongan.")
            else: 
                st.warning("Belum ada data lowongan yang aktif.")
        except Exception as e: 
            st.error(f"Menunggu sinkronisasi data dari sistem.")

    with t_ai:
        st.markdown("#### 🧠 Analisis CV & Spesifikasi Pekerjaan")
        st.info("Status Sistem: Mesin NLP disiapkan untuk iterasi berikutnya (Setelah ribuan CV masuk).")

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

    with t_profil:
        st.markdown("#### ⚙️ Pengaturan Profil Admin")
        admin_data = supabase.table("profiles").select("*").eq("id", st.session_state.user.id).execute().data[0]
        c_prof1, c_prof2 = st.columns(2)
        with c_prof1:
            upd_name = st.text_input("Nama Lengkap", value=admin_data.get('full_name', ''))
            upd_phone = st.text_input("Nomor Telepon", value=admin_data.get('phone_number', '') or '')
            if st.button("Simpan Profil"):
                supabase.table("profiles").update({"full_name": upd_name, "phone_number": upd_phone}).eq("id", st.session_state.user.id).execute()
                muat_profil(); st.success("Disimpan!"); st.rerun()

# ================= AREA DASBOR PELAMAR =================
elif st.session_state.user and st.session_state.role == "applicant":
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
    
    t_loker, t_lamaran = st.tabs(["🔍 Lowongan Terbuka", "📁 Status Lamaran Saya"])
    
    with t_loker:
        try:
            jobs_public = supabase.table("jobs").select("*").eq("is_open", True).order("created_at", desc=True).execute().data
            if jobs_public:
                for job in jobs_public:
                    with st.expander(f"🏢 {job['title']} (Dibutuhkan: {job['headcount']} Posisi)"):
                        st.write("**Deskripsi Pekerjaan:**")
                        st.write(job['job_description'])
                        st.write("**Spesifikasi Khusus:**")
                        st.write(job['job_specification'])
                        st.divider()
                        
                        cek_lamaran = supabase.table("applications").select("id").eq("job_id", job['id']).eq("applicant_id", st.session_state.user.id).execute()
                        
                        if cek_lamaran.data:
                            st.success("✅ Anda telah mengirimkan lamaran untuk posisi ini. Silakan cek tab 'Status Lamaran Saya'.")
                        else:
                            st.markdown("##### Kirimkan Lamaran Anda")
                            with st.form(f"form_lamar_{job['id']}"):
                                cv_file = st.file_uploader("Unggah Curriculum Vitae (PDF maksimal 5MB)", type=['pdf'])
                                
                                if st.form_submit_button("Kirim Dokumen & Lamar", type="primary"):
                                    if cv_file:
                                        with st.spinner("Sedang memproses dokumen Anda secara aman..."):
                                            try:
                                                file_name = f"{st.session_state.user.id}_{job['id']}.pdf"
                                                supabase.storage.from_("cv_uploads").upload(
                                                    path=file_name,
                                                    file=cv_file.getvalue(),
                                                    file_options={"content-type": "application/pdf"}
                                                )
                                                cv_url = supabase.storage.from_("cv_uploads").get_public_url(file_name)
                                                supabase.table("profiles").update({"cv_url": cv_url}).eq("id", st.session_state.user.id).execute()
                                                
                                                first_stage = supabase.table("stages").select("id").eq("job_id", job['id']).order("sequence_order").limit(1).execute()
                                                stage_id = first_stage.data[0]['id'] if first_stage.data else None
                                                
                                                supabase.table("applications").insert({
                                                    "job_id": job['id'],
                                                    "applicant_id": st.session_state.user.id,
                                                    "current_stage_id": stage_id,
                                                    "status": "active"
                                                }).execute()
                                                
                                                st.success("Lamaran berhasil terkirim!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Gagal mengirim file. Pastikan Anda sudah membuat bucket 'cv_uploads' berstatus Public di Supabase Storage. (Log: {e})")
                                    else:
                                        st.warning("Anda diwajibkan untuk mengunggah file CV (PDF).")
            else:
                st.info("Belum ada lowongan yang dibuka saat ini.")
        except Exception as e:
            st.error("Gagal memuat sistem Portal Karir.")

    with t_lamaran:
        st.markdown("#### ⏳ Riwayat dan Status Proses")
        try:
            my_apps = supabase.table("applications").select("id, status, applied_at, jobs(title), stages(stage_name)").eq("applicant_id", st.session_state.user.id).order("applied_at", desc=True).execute().data
            if my_apps:
                df_myapps = []
                for app in my_apps:
                    df_myapps.append({
                        "Posisi yang Dilamar": app['jobs']['title'],
                        "Tanggal Melamar": app['applied_at'].split("T")[0],
                        "Tahap Seleksi Saat Ini": app['stages']['stage_name'] if app['stages'] else "Menunggu Proses",
                        "Status Berkas": "🟢 AKTIF" if app['status'] == "active" else "🔴 SELESAI"
                    })
                st.dataframe(pd.DataFrame(df_myapps), use_container_width=True)
            else:
                st.info("Anda belum melamar ke posisi manapun. Silakan eksplorasi lowongan pada tab di sebelah kiri.")
        except Exception as e:
            st.error("Gagal memuat data riwayat lamaran.")
