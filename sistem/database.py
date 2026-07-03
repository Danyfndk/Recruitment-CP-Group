import streamlit as st
from supabase import create_client, Client

# Fungsi ini bertugas memanggil kunci rahasia secara aman 
# saat website dinyalakan nanti
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets[https://lwiuemxgjttpirylkyem.supabase.co/rest/v1/]
    key = st.secrets[sb_publishable_inPtlUjjFbAeOv49YkU07Q_AaCnxMrX]
    return create_client(url, key)

# Menyalakan mesin database
supabase = init_connection()
