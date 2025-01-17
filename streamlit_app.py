import streamlit as st
import pandas as pd

# Konfigurasi halaman untuk memperluas ukuran aplikasi
st.set_page_config(
    page_title="Tracking Data Excel",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
            uploaded_file = st.file_uploader(f"{hospital_name}", type=["xlsx", "xls"], key=f"{phase_name}_{hospital_name}")
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
st.markdown("---")  # Garis pembatas setelah Phase 4

# Menggabungkan semua file yang diunggah dari semua phase
all_uploaded_files = pilot_files + phase1_files + phase2_files + phase3_files + phase4_files

# Fungsi untuk membaca sheet dari file Excel
def load_sheets(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        return xls.sheet_names
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
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

    # Mengganti nilai True menjadi 1 dan False menjadi 0 pada kolom 'Is Active'
    if "Is Active" in df.columns:
        df["Is Active"] = df["Is Active"].replace({True: 1, False: 0})

    return df

# Memproses file yang diunggah
if all_uploaded_files:
    combined_data = pd.DataFrame()  # DataFrame untuk menampung data gabungan

    for hospital_name, uploaded_file in all_uploaded_files:
        st.write(f"Proses file untuk {hospital_name} - {uploaded_file.name}")

        sheet_names = load_sheets(uploaded_file)
        if not sheet_names:
            st.warning(f"Tidak ada sheet yang ditemukan dalam file {uploaded_file.name}.")
            continue

        selected_sheet = st.selectbox(f"Pilih sheet untuk {hospital_name} - {uploaded_file.name}:", sheet_names, key=f"sheet_{hospital_name}_{uploaded_file.name}")

        # Baca data dari sheet yang dipilih
        try:
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

            # Memeriksa apakah baris pertama kosong dan jika ya, menjadikan baris kedua sebagai header
            if df.iloc[0].isnull().all():
                df.columns = df.iloc[1]  # Menjadikan baris kedua sebagai header
                df = df.drop([0, 1])  # Menghapus baris pertama dan kedua yang tidak perlu

            # Menstandarisasi nama kolom
            df = standardize_columns(df)

            # Tambahkan nama rumah sakit ke data
            df["Hospital Name"] = hospital_name

            # Jika DataFrame gabungan kosong, langsung assign
            if combined_data.empty:
                combined_data = df
            else:
                # Gabungkan data berdasarkan kesamaan kolom
                combined_data = pd.concat([combined_data, df], ignore_index=True, join="inner")
        except Exception as e:
            st.error(f"Gagal memproses file {uploaded_file.name} - {e}")

    # Menyaring data berdasarkan nilai `Is Active` = 1
    if "Is Active" in combined_data.columns:
        combined_data_active = combined_data[combined_data["Is Active"] == 1]
    else:
        st.warning("Kolom 'Is Active' tidak ditemukan dalam data.")
        combined_data_active = combined_data  # Jika kolom tidak ditemukan, tetap tampilkan semua data

    # Menampilkan data dengan `Is Active` = 1
    st.write("Data Gabungan dengan 'Is Active' = 1:")
    st.dataframe(combined_data_active, use_container_width=True)

    # Menampilkan data dengan `To Be = None`
    if "To Be" in combined_data.columns:
        combined_data_none_to_be = combined_data[combined_data["To Be"].isnull()]
        st.write("Data Gabungan dengan 'To Be' = None:")
        st.dataframe(combined_data_none_to_be, use_container_width=True)

        # Menampilkan data dengan `To Be = None` dan `Is Active = 1`
        combined_data_none_to_be_active = combined_data_none_to_be[combined_data_none_to_be["Is Active"] == 1]
        st.write("Data Gabungan dengan 'To Be' = None dan 'Is Active' = 1:")
        st.dataframe(combined_data_none_to_be_active, use_container_width=True)
    else:
        st.warning("Kolom 'To Be' tidak ditemukan dalam data.")
else:
    st.info("Unggah file untuk melanjutkan.")
