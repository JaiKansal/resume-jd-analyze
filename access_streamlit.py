import streamlit as st
import psycopg2

db_url = st.secrets["database"]["DATABASE_URL"]
conn = psycopg2.connect(db_url)
# Use conn as needed...
