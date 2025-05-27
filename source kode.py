import pandas as pd
import os
import pyfiglet 
from tabulate import tabulate


def hiasan(apa):
    print(pyfiglet.figlet_format(apa, font='small'))

def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
        
def cek(dicek):
    try:
        if not dicek.strip():
            raise ValueError("Tidak boleh kosong")
        elif dicek.isdigit():
            raise ValueError("Harus berupa huruf")
        else:
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
        else:
            return angka
    except ValueError as e:
        print(e)
        return False
    

akun = "user.csv"
def register():
    while True:
        nama = input("Masukkan nama : ")
        if cek(nama) == False:
            continue
        else:
            break
    while True:
        while True:
            no_wa = input("Masukkan nomor whatsapp : ")
            if dicek(no_wa) == False:
                continue
            else:
                break
        if not no_wa.startswith("62"):
            print("Nomor harus berawal 62")
        elif len(no_wa) < 8:
            print("Nomor harus lebih dari 8 digit")
        else:
            break
    while True:
        kecamatan = input("asal kecamatan : ")
        if cek(kecamatan) == False:
            continue
        else:
            break
    bukadb = pd.read_csv(akun)
    while True: 
        username = input("Buat username : ")
        if username.strip() in bukadb['Username'].str.strip().values:
            print("Username tidak boleh kosong")
            continue
        if username in bukadb['Username'].values:
            print("Username telah terdaftar, buat yang lain")
        else:
            break
    while True:
        password = input("Buat pasword : ")
        if not password.strip():
            print("Password tidak boleh kosong")
        else:
            break
    ID = bukadb['ID'].max()
    ID += 1
    baru = pd.DataFrame({'ID':[ID],'Nama':[nama],'Kecamatan': [kecamatan],'Nomor WA': [no_wa],'Username': [username],'Password': [password],'Role': ['user']})
    baru.to_csv(akun, mode='a', header=False, index=False)
    hiasan("Registrasi berhasil")
    input("Tekan enter untuk melanjutkan")
    clear_terminal()

def login():
    while True:
        username = input("Masukkan username : ").strip()
        if cek(username) == False:
            continue
        else:
            break
    password = input("Masukkan password : ").strip()
    bukadb = pd.read_csv(akun)

    bukadb['Username'] = bukadb['Username'].astype(str).str.strip()
    bukadb['Password'] = bukadb['Password'].astype(str).str.strip()

    if username in bukadb['Username'].values:
        sebaris = bukadb[bukadb["Username"] == username]
        if sebaris['Password'].values[0] == password:
            hiasan("Login berhasil")
            input("Tekan enter untuk melanjutkan")
            clear_terminal()
            role = sebaris['Role'].values[0]           
            id_user = sebaris["ID"].values[0]
            nama = sebaris["Nama"].values[0]
            Menu(role,id_user,nama)
        else:
            hiasan("Password salah")
            input("Tekan enter untuk melanjutkan")
            clear_terminal()
    else:        
        hiasan("Akun belum terdaftar")
        input("Tekan enter untuk melanjutkan")
        clear_terminal()
        
def Menu(role,id_user,nama):
    while True:       
        if role == "user":
            pilihan = input("Menu yang dipilih : ")
        else:
            pilihan = input("Menu yang dipilih : ")
            
while True:
    hiasan("Selamat datang di Buildflow")
    print("""
1. Login
2. Register
3. Keluar""")
    pilih = input("Silahkan pilih : ")
    if pilih == '1':
        login()
    elif pilih == '2':
        register()
    elif pilih == '3':
        clear_terminal()
        break
    else:
        clear_terminal()
        print("Pilihan yang kamu masukkan tidak sesuai")