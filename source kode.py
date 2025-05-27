import pandas as pd
import os
import pyfiglet
from tabulate import tabulate

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

def cari_kecamatan(nama_kecamatan):
    try:
        data_kecamatan = pd.read_csv("kecamatan.csv")
        return data_kecamatan[data_kecamatan['Kecamatan'].str.lower().str.contains(nama_kecamatan.lower())]
    except FileNotFoundError:
        print("Database kecamatan tidak ditemukan.")
        return pd.DataFrame()

def tambah_kecamatan(nama_baru):
    try:
        data_kecamatan = pd.read_csv("kecamatan.csv")
    except FileNotFoundError:
        data_kecamatan = pd.DataFrame(columns=['ID', 'Kecamatan'])
    
    if nama_baru.lower() in data_kecamatan['Kecamatan'].str.lower().values:
        print("Kecamatan sudah ada di database.")
        return
    
    next_id = 1 if data_kecamatan.empty else data_kecamatan['ID'].max() + 1
    data_baru = pd.DataFrame({'ID': [next_id], 'Kecamatan': [nama_baru.title()]})
    data_kecamatan = pd.concat([data_kecamatan, data_baru], ignore_index=True)
    data_kecamatan.to_csv("kecamatan.csv", index=False)
    print(f"Kecamatan '{nama_baru.title()}' berhasil ditambahkan dengan ID {next_id}.")

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

        # ini nanti buat biar si admin bisa nambahin nama kecamtan baru, kalo ini cuma pas csvnya kosong baru disuruh masukin
        hasil = cari_kecamatan(cari)
        if hasil.empty:
            print("Kecamatan tidak ditemukan.")
            tambah = input("Apakah ingin menambah kecamatan baru? (y/n): ").lower()
            if tambah == 'y':
                nama_baru = input("Masukkan nama kecamatan baru: ").strip()
                if nama_baru:
                    tambah_kecamatan(nama_baru)
                else:
                    print("Nama kecamatan tidak boleh kosong.")
            continue
        else:
            hasil['Kecamatan'] = hasil['Kecamatan'].str.title()
            print("\nHasil pencarian:")
            print(tabulate(hasil, headers='keys', tablefmt='fancy_grid'))
            try:
                id_kec = int(input("Masukkan ID kecamatan anda dari hasil di atas: "))
                if id_kec in hasil['ID'].values:
                    return hasil.loc[hasil['ID'] == id_kec, 'Kecamatan'].values[0]
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

    ID = bukadb['ID'].max() + 1 if not bukadb.empty else 1
    baru = pd.DataFrame([{
        'ID': ID,
        'Nama': nama,
        'Kecamatan': kecamatan,
        'Nomor WA': no_wa,
        'Username': username,
        'Password': password,
        'Role': 'customer'
    }])
    baru.to_csv(akun, mode='a', header=not os.path.exists(akun), index=False)
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
        if role == "Customer":
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
                6: "Hapus Riwayat Transaksi Customer",
                7: "Lihat Angkutan" 
                }
            
            for key, value in menu_admin.items():
                print(f"{key}. {value}")

        pilihan = input("Pilih menu: ").strip()
        if pilihan == '2':
            clear_terminal()
            break
        elif pilihan == '1':
            print("Data belum tersedia.")
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
