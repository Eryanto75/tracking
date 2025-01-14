import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Konfigurasi halaman untuk memperluas ukuran aplikasi
st.set_page_config(
    page_title="Tracking Data Excel",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Fungsi untuk memverifikasi login
def verify_login(username, password):
    # Daftar pengguna dan kata sandi yang diizinkan
    allowed_users = {"ade": "masde", "admin": "dpim"}
    return allowed_users.get(username) == password

# Tampilkan form login
st.sidebar.title("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if verify_login(username, password):
        st.sidebar.success("Login successful")

        # Judul aplikasi
        st.title("Tracking Data Excel - Unggah File untuk Rumah Sakit Berdasarkan Phase")

        # Nama rumah sakit untuk setiap phase
        phase1_names = ["MRCCC", "SHBG", "SHBP", "SHKJ", "SHLC", "SHMD", "SHPL", "SHSB", "SHTB"]
        phase2_names = ["ASRI", "SHAB", "SHJB", "SHKP", "SHMA", "SHMN", "SHPD", "SHYG"]
        phase3_names = ["RSUSKD", "SHAG", "SHBB", "SHBJ", "SHBS", "SHBT", "SHCN", "SHJR", "SHLL", "SHPR", "SHSR", "SHST"]
        phase4_names = ["BIMC KT", "BIMC ND", "RSUS", "RSUSW", "SHBN", "SHCB", "SHDP", "SHMT", "SHPW"]
        pilot_names = ["SHLB", "SHLV", "SHMK"]

        # Fungsi untuk membuat grid file uploader per phase
        def create_phase_uploaders(phase_name, hospital_names):
            st.subheader(phase_name)
            cols = st.columns(4)
            uploaded_files = []
            for i, hospital_name in enumerate(hospital_names):
                with cols[i % 4]:
                    uploaded_file = st.file_uploader(f"{hospital_name}", type=["xlsx", "xls"], key=f"{phase_name}_{hospital_name}_uploader")
                    if uploaded_file:
                        uploaded_files.append((hospital_name, uploaded_file))
            return uploaded_files

        # Mengelompokkan file unggahan berdasarkan phase
        pilot_files = create_phase_uploaders("Pilot", pilot_names)
        st.markdown("---")  # Garis pembatas setelah Pilot
        phase1_files = create_phase_uploaders("Phase 1", phase1_names)
        st.markdown("---")  # Garis pembatas setelah Phase 1
        phase2_files = create_phase_uploaders("Phase 2", phase2_names)
        st.markdown("---")  # Garis pembatas setelah Phase 2
        phase3_files = create_phase_uploaders("Phase 3", phase3_names)
        st.markdown("---")  # Garis pembatas setelah Phase 3
        phase4_files = create_phase_uploaders("Phase 4", phase4_names)

        # Menggabungkan semua file yang diunggah dari semua phase
        all_uploaded_files = pilot_files + phase1_files + phase2_files + phase3_files + phase4_files

        # Fungsi untuk membaca sheet dari file Excel
        def load_sheets(uploaded_file):
            try:
                xls = pd.ExcelFile(uploaded_file)
                return xls.sheet_names
            except Exception as e:
                st.error(f"Gagal membaca sheet dari file: {e}")
                return []

        # Menstandarisasi nama kolom
        def standardize_columns(df):
            column_mapping = {
                'code': 'Code',
                'name': 'Name',
                'notes': 'Notes',
                'admission type id': 'Admission Type Id',
                'service line id': 'Service Line Id',
                'to be': 'To Be',
                'is active': 'Is Active',
                'hospital name': 'Hospital Name'
            }
            # Mengubah kolom yang ada menjadi format standar
            df = df.rename(columns=lambda x: x.strip().lower())
            df = df.rename(columns=column_mapping)
            return df

        # Memproses file yang diunggah
        if all_uploaded_files:
            combined_data = pd.DataFrame()  # DataFrame untuk menampung data gabungan

            for hospital_name, uploaded_file in all_uploaded_files:
                st.write(f"Proses file untuk {hospital_name} - {uploaded_file.name}")

                sheet_names = load_sheets(uploaded_file)
                if not sheet_names:
                    continue

                selected_sheet = st.selectbox(f"Pilih sheet untuk {hospital_name} - {uploaded_file.name}:", sheet_names, key=f"sheet_{hospital_name}_{uploaded_file.name}")

                try:
                    # Baca data dari sheet yang dipilih
                    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                    # Menstandarisasi nama kolom
                    df = standardize_columns(df)
                    # Tambahkan nama rumah sakit ke data
                    df["Hospital Name"] = hospital_name

                    # Gabungkan data berdasarkan kesamaan kolom
                    if combined_data.empty:
                        combined_data = df
                    else:
                        common_columns = set(combined_data.columns).intersection(df.columns)
                        df = df[list(common_columns)]
                        combined_data = pd.concat([combined_data, df], ignore_index=True)
                except Exception as e:
                    st.error(f"Error membaca data dari file {uploaded_file.name}: {e}")

            # Tampilkan data gabungan
            if not combined_data.empty:
                st.write("Data Gabungan dari Semua File:")
                st.dataframe(combined_data, use_container_width=True)

                # Menghitung jumlah nilai null di kolom "To Be"
                if "To Be" in combined_data.columns:
                    null_counts_by_hospital = combined_data.groupby("Hospital Name")["To Be"].apply(lambda x: x.isnull().sum())

                    # Mengurutkan jumlah nilai null dari yang terbanyak
                    null_counts_by_hospital_sorted = null_counts_by_hospital.sort_values(ascending=False)

                    # Visualisasi barchart untuk jumlah nilai null
                    if not null_counts_by_hospital_sorted.empty:
                        st.subheader("Jumlah Nilai Null pada Kolom 'To Be' per Rumah Sakit")

                        fig, ax = plt.subplots(figsize=(10, 6))
                        null_counts_by_hospital_sorted.plot(kind='bar', ax=ax, color='skyblue')
                        ax.set_ylabel('Jumlah Nilai Null')
                        ax.set_title('Jumlah Nilai Null pada Kolom "To Be" per Rumah Sakit')
                        plt.xticks(rotation=45, ha="right")
                        st.pyplot(fig)

                    # Menampilkan tabel terpisah untuk 'Code' dan 'Admission Type Id'
                    st.subheader("Data dengan Nilai Null pada Kolom 'To Be'")
                    null_data = combined_data[combined_data['To Be'].isnull()]
                    null_table = null_data[['Code', 'Admission Type Id', 'Hospital Name']].drop_duplicates()
                    st.dataframe(null_table)
                else:
                    st.warning("Kolom 'To Be' tidak ditemukan dalam data.")

                # Unduh data gabungan sebagai CSV
                combined_csv = combined_data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Data Gabungan",
                    data=combined_csv,
                    file_name="tracking_data.csv",
                    mime="text/csv"
                )
            else:
                st.info("Tidak ada data yang berhasil digabungkan.")
        else:
            st.info("Unggah file untuk melanjutkan.")
    else:
        st.sidebar.error("Invalid username or password")
