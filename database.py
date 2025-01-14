import sqlite3

# Fungsi untuk membuat koneksi ke database SQLite
def create_connection(db_name="upload_files.db"):
    conn = sqlite3.connect(db_name)
    return conn

# Fungsi untuk membuat tabel jika belum ada
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Membuat tabel untuk menyimpan metadata file
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_name TEXT,
        file_name TEXT,
        sheet_name TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Fungsi untuk menyimpan metadata file yang diunggah
def save_file_to_db(hospital_name, file_name, sheet_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO uploaded_files (hospital_name, file_name, sheet_name)
    VALUES (?, ?, ?)
    ''', (hospital_name, file_name, sheet_name))
    
    conn.commit()
    conn.close()

# Fungsi untuk menghapus data dari database berdasarkan ID
def delete_file_from_db(file_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM uploaded_files WHERE id = ?
    ''', (file_id,))
    
    conn.commit()
    conn.close()