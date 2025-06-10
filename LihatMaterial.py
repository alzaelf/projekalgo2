import pandas as pd
from tabulate import tabulate

def selection_sort(data):
    for i in range(len(data)):
        min_index = i
        for j in range(i + 1, len(data)):
            if data[j]['Material'].lower() < data[min_index]['Material'].lower():
                min_index = j
        data[i], data[min_index] = data[min_index], data[i]
    return data
 
def linear_search(data, keyword):
    result = []
    for row in data:
        if keyword.lower() in row['Material'].lower():
            result.append(row)
    return result

def LIhat_Material():
    try:
        df = pd.read_csv("material_dummy.csv")
    except FileNotFoundError:
        print("File material.csv tidak ditemukan.")
        return

    data = df.to_dict(orient='records')
    data = selection_sort(data)

    while True:
        print("\nDaftar Material")
        print(tabulate(data, headers="keys", tablefmt="fancy_grid"))

        cari = input("\nMasukkan nama material yang ingin dicari (atau kosongkan untuk kembali): ").strip()
        if not cari:
            break

        hasil = linear_search(data, cari)
        if hasil:
            print("\nHasil Pencarian:")
            print(tabulate(hasil, headers="keys", tablefmt="fancy_grid"))
        else:
            print("Material tidak ditemukan.")