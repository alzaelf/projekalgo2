import pandas as pd
import os
import csv
import pyfiglet
from LihatMaterial import Lihat_Material
from hapusbarang import hapus_barang
from tambahmaterial import tambah_material
from angkutan import kelola_angkutan
from tabulate import tabulate
from UbahMaterial import UbahMaterial
from transaction import Transaction

def hiasan(apa):
    print(pyfiglet.figlet_format(apa, font='small'))

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def cek(dicek):
    try:
        if not dicek.strip():
            raise ValueError("Tidak boleh kosong")
        elif dicek.isdigit():
            raise ValueError("Harus berupa huruf")
        return dicek
    except ValueError as e:
        print(e)
        return False

def dicek(angka):
    try:
        if not angka.strip():
            raise ValueError("Tidak boleh kosong")
        elif angka.isalpha():
            raise ValueError("Harus berupa angka")
        return angka
    except ValueError as e:
        print(e)
        return False
    
def lihat_kecamatan():
    try:
        df = pd.read_csv("kecamatan.csv")
        if 'Kecamatan' in df.columns:
            df['Kecamatan'] = df['Kecamatan'].str.title()
            print(tabulate(df, headers='keys', tablefmt='fancy_grid'))
        else:
            print("Kolom 'Kecamatan' tidak ditemukan.")
    except FileNotFoundError:
        print("File 'kecamatan.csv' tidak ditemukan.")
    
    input("\nTekan enter untuk kembali ke menu...")

def cari_kecamatan(nama_kecamatan):
    hasil = []
    try:
        with open("kecamatan.csv", mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)

            if 'Kecamatan' not in header:
                print("Kolom 'Kecamatan' tidak ditemukan dalam file CSV.")
                return []

            index_kecamatan = header.index('Kecamatan')
            kata_kunci = nama_kecamatan.lower().strip()

            for baris in reader:
                if len(baris) > index_kecamatan:
                    nama_data = baris[index_kecamatan].strip().lower()
                    if kata_kunci in nama_data:
                        hasil.append([baris[0].strip(), baris[index_kecamatan].strip().title()])

        return hasil

    except FileNotFoundError:
        print("File kecamatan.csv tidak ditemukan.")
        return []

def pilih_kecamatan():
    while True:
        cari = input("Cari nama kecamatan anda (atau ketik 'lihat' untuk daftar semua): ").strip()
        try:
            data_kecamatan = pd.read_csv("kecamatan.csv")
        except FileNotFoundError:
            print("File 'kecamatan.csv' tidak ditemukan.")
            return None

        if cari.lower() == 'lihat':
            data_kecamatan['Kecamatan'] = data_kecamatan['Kecamatan'].str.title()
            print(tabulate(data_kecamatan, headers='keys', tablefmt='fancy_grid'))
            continue

        hasil = cari_kecamatan(cari)
        if not hasil:
            print("Kecamatan tidak ditemukan.")
            continue

        hasil_df = pd.DataFrame(hasil, columns=["ID", "Kecamatan"])
        print("\nHasil Pencarian:")
        print(tabulate(hasil_df, headers='keys', tablefmt='fancy_grid'))

        try:
            id_kec = int(input("Masukkan ID kecamatan anda dari hasil di atas: "))
            if id_kec in hasil_df['ID'].astype(int).values:
                return hasil_df.loc[hasil_df['ID'].astype(int) == id_kec, 'Kecamatan'].values[0]
            else:
                print("ID tidak valid.")
        except ValueError:
            print("Masukkan hanya angka untuk ID.")

akun = "user.csv"

def register():
    while True:
        nama = input("Masukkan nama: ")
        if not cek(nama): continue
        break

    while True:
        no_wa = input("Masukkan nomor WhatsApp: ")
        if not dicek(no_wa): continue
        if not no_wa.startswith("62"):
            print("Nomor harus diawali dengan 62.")
        elif len(no_wa) < 8:
            print("Nomor harus lebih dari 8 digit.")
        else:
            break

    kecamatan = pilih_kecamatan()
    if kecamatan is None:
        return

    try:
        bukadb = pd.read_csv(akun)
    except FileNotFoundError:
        bukadb = pd.DataFrame(columns=['ID', 'Nama', 'Kecamatan', 'Nomor WA', 'Username', 'Password', 'Role'])

    while True:
        username = input("Buat username: ").strip()
        if not username:
            print("Username tidak boleh kosong.")
            continue
        if username in bukadb['Username'].values:
            print("Username telah terdaftar, buat yang lain.")
        else:
            break

    while True:
        password = input("Buat password: ").strip()
        if not password:
            print("Password tidak boleh kosong.")
        else:
            break
        
    bukadb.loc[len(bukadb) +1] = [
        bukadb['ID'].max() + 1 if not bukadb.empty else 1,
        nama,
        kecamatan,
        no_wa,
        username,
        password,
        'Customer'
    ]

    bukadb.to_csv(akun, index=False)
    hiasan("Registrasi berhasil")
    input("Tekan enter untuk melanjutkan")
    clear_terminal()

def login():
    while True:
        username = input("Masukkan username: ").strip()
        if not cek(username): continue
        break
    password = input("Masukkan password: ").strip()

    try:
        bukadb = pd.read_csv(akun)
    except FileNotFoundError:
        print("Belum ada data akun.")
        return

    bukadb['Username'] = bukadb['Username'].astype(str).str.strip()
    bukadb['Password'] = bukadb['Password'].astype(str).str.strip()

    if username in bukadb['Username'].values:
        sebaris = bukadb[bukadb['Username'] == username]
        if sebaris['Password'].values[0] == password:
            hiasan("Login berhasil")
            input("Tekan enter untuk melanjutkan")
            clear_terminal()
            role = sebaris['Role'].values[0]
            id_user = sebaris['ID'].values[0]
            nama = sebaris['Nama'].values[0]
            Menu(role, id_user, nama)
        else:
            hiasan("Password salah")
            input("Tekan enter untuk melanjutkan")
            clear_terminal()
    else:
        hiasan("Akun belum terdaftar")
        input("Tekan enter untuk melanjutkan")
        clear_terminal()

def Menu(role, id_user, nama):
    while True:
        hiasan(f"Menu {role.capitalize()}")

        transaction = Transaction(id_user)

        if role.lower() == "customer":
            print(f"Halo {nama}! (ID: {id_user})")
            menu_customer = {
                1: "Lihat Material",
                2: "Beli Material",
                3: "Lihat Riwayat Transaksi",
                4: "Logout" 
                }
            
            for key, value in menu_customer.items():
                print(f"{key}. {value}")
        else:
            menu_admin = {
                1: "Lihat Material",
                2: "Tambah Material",
                3: "Hapus Material",
                4: "Ubah Data Material",
                5: "Lihat Riwayat Transaksi Customer",
                6: "Kelola Angkutan",
                7: "Lihat Data Kecamatan",
                8: "Logout"
                }
            
            for key, value in menu_admin.items():
                print(f"{key}. {value}")

        pilihan = input("Pilih menu: ").strip()
        if pilihan == '1':
            Lihat_Material()

        elif pilihan == '2':
            if role.lower() == 'customer':
                transaction.CreateTransactionMenu()
            elif role.lower() == 'admin':
                tambah_material()
                
        elif pilihan == '3':
            if role.lower() == 'customer':
                transaction.ShowAllTransaction()
            elif role.lower() == 'admin':
                hapus_barang()

        elif pilihan == '4':
            if role.lower() == 'customer':
                print("Logout berhasil. Kembali ke menu utama...")
                break 
            elif role.lower() == 'admin':
                UbahMaterial()

        elif pilihan == '5' and role.lower() == 'admin':
                transaction.ShowAllTransaction()

        elif pilihan == '6' and role.lower() == 'admin':
                kelola_angkutan()

        elif pilihan == '7' and role.lower() == 'admin':
                lihat_kecamatan()

        elif pilihan == '8' and role.lower() == 'admin':
                clear_terminal()
                break
        else:
            print("Pilihan tidak valid.")

while True:
    hiasan("Selamat datang di Buildflow")
    print("""
1. Login
2. Register
3. Keluar""")
    pilih = input("Silahkan pilih: ").strip()
    if pilih == '1':
        login()
    elif pilih == '2':
        register()
    elif pilih == '3':
        clear_terminal()
        break
    else:
        clear_terminal()
        print("Pilihan yang kamu masukkan tidak sesuai.")