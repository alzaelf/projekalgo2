import pandas as pd
from tabulate import tabulate
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

    print("\nData Material Saat Ini:")
    print(tabulate(data[['ID', 'Material', 'Stock']], headers='keys', tablefmt='fancy_grid', showindex=False))

    pilihan = input("\nHapus berdasarkan (1) ID atau (2) Nama? (1/2): ").strip()
    if pilihan == '1':
        try:
            id_hapus = int(input("Masukkan ID material yang ingin dihapus: "))
            if id_hapus in data['ID'].values:
                data = data[data['ID'] != id_hapus]
                data.to_csv(filename, index=False)
                print(f"\nMaterial dengan ID {id_hapus} berhasil dihapus.")
            else:
                print("\nID tidak ditemukan.")
        except ValueError:
            print("\nID harus berupa angka.")
    elif pilihan == '2':
        nama_hapus = input("Masukkan nama material yang ingin dihapus: ").strip().title()
        if nama_hapus in data['Material'].astype(str).str.title().values:
            data = data[data['Material'].str.title() != nama_hapus]
            data.to_csv(filename, index=False)
            print(f"\nMaterial '{nama_hapus}' berhasil dihapus.")
        else:
            print("\nNama material tidak ditemukan.")
    else:
        print("\nPilihan tidak valid.")

    # Tampilkan data terbaru setelah dihapus
    print("\nData Material Setelah Penghapusan:")
    if not data.empty:
        print(tabulate(data[['ID', 'Material', 'Stock']], headers='keys', tablefmt='fancy_grid', showindex=False))
    else:
        print("Data material kosong.")

    input("\nTekan Enter untuk kembali...")