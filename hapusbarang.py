import pandas as pd
import os

def hapus_barang(filename="material_dummy.csv"):
    if not os.path.exists(filename):
        print("File data material tidak ditemukan.")
        return

    try:
        data = pd.read_csv(filename)
    except Exception as e:
        print(f"Gagal membaca file: {e}")
        return

    if data.empty:
        print("Data material kosong.")
        return

    print("Data Material Saat Ini:")
    print(data[['ID', 'Material', 'Stock']].to_string(index=False))

    pilihan = input("Hapus berdasarkan (1) ID atau (2) Nama? (1/2): ").strip()
    if pilihan == '1':
        try:
            id_hapus = int(input("Masukkan ID material yang ingin dihapus: "))
            if id_hapus in data['ID'].values:
                data = data[data['ID'] != id_hapus]
                data.to_csv(filename, index=False)
                print(f"Material dengan ID {id_hapus} berhasil dihapus.")
            else:
                print("ID tidak ditemukan.")
        except ValueError:
            print("ID harus berupa angka.")
    elif pilihan == '2':
        nama_hapus = input("Masukkan nama material yang ingin dihapus: ").strip().title()
        if nama_hapus in data['Material'].astype(str).str.title().values:
            data = data[data['Material'].str.title() != nama_hapus]
            data.to_csv(filename, index=False)
            print(f"Material '{nama_hapus}' berhasil dihapus.")
        else:
            print("Nama material tidak ditemukan.")
    else:
        print("Pilihan tidak valid.")
    
    input("Tekan Enter untuk kembali...")