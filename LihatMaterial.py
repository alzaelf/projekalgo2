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

def Lihat_Material(): 
    try:
        df = pd.read_csv("material_dummy.csv") 
    except FileNotFoundError: 
        print("File material_dummy.csv tidak ditemukan.")
        return 

    if 'Material' not in df.columns: 
        print("Kolom 'Material' tidak ditemukan dalam file.")
        return

    data = df.to_dict(orient='records')  
    data = selection_sort(data) 
    datas = pd.DataFrame(data)  

    print("\nDaftar Material Tersedia:") 
    print(tabulate(datas.loc[:, ['Material', 'Price', 'Stock', 'Volume']], headers="keys", tablefmt="fancy_grid"))  

    while True:  
        cari = input("\nMasukkan nama material yang ingin dicari (atau kosongkan untuk kembali): ").strip()  # Input keyword pencarian
        if not cari:  
            print("Kembali ke menu sebelumnya...")  
            break

        hasil = linear_search(data, cari)  
        if hasil:  
            print("\nHasil Pencarian:")
            filtered = [{k: row[k] for k in ['Material', 'Price', 'Stock', 'Volume']} for row in hasil]
            print(tabulate(filtered, headers="keys", tablefmt="fancy_grid"))
        else:
            print("Material tidak ditemukan.")