import streamlit as st
import pandas as pd
from database import save_file_to_db, delete_file_from_db, create_connection, create_table

# Pastikan tabel ada sebelum aplikasi dijalankan
create_table()

def load_sheets(uploaded_file):
    # Fungsi untuk mendapatkan nama sheet dari file Excel
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        return excel_file.sheet_names
    except Exception as e:
        st.error(f"Gagal membaca sheet: {e}")
        return []

def standardize_columns(df):
    # Fungsi untuk menstandarisasi nama kolom (misal untuk keseragaman)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

# Antarmuka Streamlit untuk mengunggah file
st.title("Unggah dan Proses Data")
uploaded_files = st.file_uploader("Pilih file Excel untuk diunggah", accept_multiple_files=True)

if uploaded_files:
    all_uploaded_files = []  # List untuk menyimpan data yang diunggah
    for uploaded_file in uploaded_files:
        hospital_name = st.text_input(f"Nama Rumah Sakit untuk file {uploaded_file.name}:")
        if hospital_name:
            sheet_names = load_sheets(uploaded_file)
            if sheet_names:
                selected_sheet = st.selectbox(f"Pilih sheet untuk {hospital_name} - {uploaded_file.name}:", sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                df = standardize_columns(df)

                # Simpan metadata file yang diunggah ke database
                save_file_to_db(hospital_name, uploaded_file.name, selected_sheet)

                st.write(f"Data dari file {uploaded_file.name} telah diproses.")
                st.dataframe(df.head())

    # Menampilkan file yang ada di database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploaded_files")
    files = cursor.fetchall()
    
    for file in files:
        st.write(f"ID: {file[0]} - Hospital: {file[1]} - File: {file[2]} - Sheet: {file[3]} - Uploaded at: {file[4]}")
        if st.button(f"Hapus {file[2]} dari database", key=f"delete_{file[0]}"):
            delete_file_from_db(file[0])
            st.success(f"File {file[2]} berhasil dihapus dari database.")

    conn.close()