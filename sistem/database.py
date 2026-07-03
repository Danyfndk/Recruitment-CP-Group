import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    # URL mutlak tanpa tambahan karakter di belakangnya
    url = "https://lwiuemxgjttpirylkyem.supabase.co"
    
    # Kunci Secret disisipkan langsung agar sistem bisa langsung diakses
    key = "sb_publishable_inPtlUjjFbAeOv49YkU07Q_AaCnxMrX"
    
    return create_client(url, key)

supabase = init_connection()
