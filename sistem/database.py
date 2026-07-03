import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    # Kunci dimasukkan secara langsung (Hardcoded)
    url = "https://lwiuemxgjttpirylkyem.supabase.co"
    key = "sb_publishable_inPt1UjjFbAeOv49YkU07Q_AaCnxMrX"
    return create_client(url, key)

supabase = init_connection()
