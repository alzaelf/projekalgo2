import pandas as pd
import os

MATERIAL_FILE = 'material_dummy.csv'

def tambah_material():
    try:
        data = pd.read_csv(MATERIAL_FILE)
    except FileNotFoundError:
        data = pd.DataFrame(columns=['ID', 'Material', 'Price', 'Stock', 'Volume'])

    while True:
        nama = input("Masukkan nama material: ").strip()
        if not nama:
            print("Nama tidak boleh kosong.")
            continue
        if nama in data['Material'].values:
            print("Material sudah ada.")
            continue
        break

    while True:
        try:
            harga = int(input("Masukkan harga material: "))
            stok = int(input("Masukkan stok material: "))
            volume = float(input("Masukkan volume material: "))
            break
        except ValueError:
            print("Harga, stok, dan volume harus berupa angka.")

    next_id = 1 if data.empty else data['ID'].max() + 1
    data.loc[len(data)] = [next_id, nama, harga, stok, volume]

    data.to_csv(MATERIAL_FILE, index=False)
    print(f"Material '{nama}' berhasil ditambahkan dengan ID {next_id}.")

if __name__ == "__main__":
    tambah_material()