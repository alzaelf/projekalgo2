import os, sys, time, re
from datetime import datetime
import pandas as pd
from tabulate import tabulate 
import json

TRANSACTION_FILE = 'transaction.csv'
DETAIL_FILE = 'detail_transaction.csv'
MATERIAL_FILE = 'material_dummy.csv'
KECAMATAN = 'sumbersari'

def GetCsv(filename, column = list):
    try:
        return pd.read_csv(filename)
    except:
        return pd.DataFrame(columns=column)

def load_graph(path = str):
    try:
        with open(path, 'r') as file:
            data = json.load(file)

        vertices = data['vertices']
        edges = data['edges']

        graph = {v:{} for v in vertices}

        for edge in edges:
            graph[edge['from']][edge['to']] = edge['weight']

        return graph

    except FileNotFoundError:
        print(f"file {path} tidak ditemukan")
        return None

# Dari source kode.py
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_float(string):
    pattern = r'^[+-]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?$'
    return bool(re.match(pattern, string))

# Dari source kode.py
def Check(inputs, type):
    try:
        if not inputs.strip():
            raise ValueError("Tidak boleh kosong")
        elif type == 'str' and inputs.isdigit():
            raise ValueError("Harus berupa huruf")
        elif type == 'num' and not inputs.isdigit() :
            raise ValueError("Harus berupa angka")
        elif type == 'flo' and not is_float(inputs):
            raise ValueError("Harus berupa float (X.X)")
        
        return inputs
    
    except ValueError as e:
        print(e)
        return False

def ClearPrevLine(lines = 1):
    for i in range(lines + 1):
        sys.stdout.write('\033[K')
        if i < lines:
            sys.stdout.write('\033[1A')
    sys.stdout.flush()

def Input(text, datatype = 'str', null=False):
    while True:
        temp = input(f'{text} : ')

        if null and not temp.split():
            return temp
            
        if not Check(temp, datatype):
            time.sleep(2)
            ClearPrevLine(2)
            continue

        return temp if datatype == 'str' \
            else int(temp) if datatype == 'num' \
                else float(temp) if datatype == 'flo' else None

def CalculateShippingCost(graph, start, finish): # Kalkulasi Ongkir (Djikstra)
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        predecessors = {node: None for node in graph}
        unvisited = set(graph.keys())
        
        while unvisited:
            # Pilih simpul dengan jarak terkecil dari unvisited
            min_distance = float('inf')
            current = None
            for node in unvisited:
                if distances[node] < min_distance:
                    min_distance = distances[node]
                    current = node
            
            if current is None:
                break
            
            if current == finish:
                break
            
            unvisited.remove(current)
            
            for neighbor, weight in graph[current].items():
                if neighbor in unvisited:
                    new_distance = distances[current] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = current

        path = []
        current = finish
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path = path[::-1]
        
        # Periksa apakah jalur valid
        if distances[finish] == float('inf'):
            print(f"Tidak ada jalur dari {start} ke {finish}")
        
        return distances[finish], path

def binary_search(data, target):
    low = 0
    high = len(data) - 1
    result_indexes = []

    while low <= high:
        mid = (low + high) // 2
        if data[mid] == target:
            # Jika ditemukan, cari semua yang punya MaterialID sama
            # Cek ke kiri
            left = mid
            while left >= 0 and data[left] == target:
                result_indexes.append(left)
                left -= 1

            # Cek ke kanan
            right = mid + 1
            while right < len(data) and data[right] == target:
                result_indexes.append(right)
                right += 1

            return sorted(result_indexes)

        elif data[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1  # Tidak ketemu

class Transaction:
    def __init__(self, userId):
        self.data = GetCsv(TRANSACTION_FILE, ['ID', 'Date', 'UserID', 'Delivery', 'Total', 'VTotal'])

        self.material = GetCsv(MATERIAL_FILE, ['ID', 'Material', 'Price', 'Stock', 'Volume'])

        self.detail = GetCsv(DETAIL_FILE, ['ID', 'TransactionID', 'MaterialID', 'Quantity', 'Subtotal', 'SubVolume'])

        user = pd.read_csv('user.csv')
        self.user = user.loc[user['ID'] == userId]

        self.graph = load_graph('kecamatan_graph.json')
        self.isAdmin = True if self.user.loc[:, 'Role'].values[0].lower() == 'admin' else False

    def ShowAllTransaction(self):
        transactions = self.data.copy()
        details = self.detail.copy()
        materials = self.material.copy()
        users = GetCsv('user.csv')
        
        if transactions.empty or details.empty or materials.empty or users.empty:
            print("Salah satu file CSV kosong.")
            return None

        # gabung detail dengan transaction
        merged_data = details.merge(transactions, left_on="TransactionID", right_on="ID", suffixes=('_detail', '_transaction'))

        # Mendapatkan nama material
        merged_data = merged_data.merge(materials[['ID', 'Material']], left_on="MaterialID", right_on="ID", suffixes=('', '_material'))

        # Mendapatkan nama user
        merged_data = merged_data.merge(users[['ID', 'Nama']], left_on="UserID", right_on="ID", suffixes=('', '_user'))

        # pilah kolom
        data = merged_data[['TransactionID', 'Material', 'Quantity', 'Subtotal', 'Date', 'Nama', 'Delivery']]
        
        data = data.copy()
        data['Subtotal'] = data['Subtotal'].astype(int)

        data['MaterialLower'] = data['Material'].str.lower()

        daftar_material = data['MaterialLower'].tolist()

        if self.isAdmin:
            print(tabulate(
            data[['TransactionID', 'Date','Material', 'Nama', 'Quantity', 'Delivery', 'Subtotal']],
            headers='keys',
            tablefmt='fancy_grid',
            showindex=False
            ))
            
            cari = input("\nMasukkan Tanggal yang ingin dicari (atau tekan Enter untuk kembali): ").strip().lower()

            if not cari:
                print("\nKembali ke menu admin...")
                return

            hasil_index = binary_search(self.data.Date , cari)

            if hasil_index != -1:
                hasil = data.iloc[hasil_index]
                print("\nData transaksi yang ditemukan:")
                print(tabulate(
                    hasil[['TransactionID', 'Date', 'Material', 'Nama', 'Quantity', 'Delivery', 'Subtotal']],
                    headers='keys',
                    tablefmt='fancy_grid',
                    showindex=False
                ))
            else:
                print(f"\nTidak ada transaksi yang ditemukan pada tanggal {cari}.")

            input("\nTekan Enter untuk kembali ke menu admin...")

        else:
            user = str(self.user['Nama'].copy().values[0])
            print(tabulate(
            data.loc[data['Nama'] == self.user['Nama'].copy().values[0], ['TransactionID', 'Date','Material', 'Quantity', 'Delivery', 'Subtotal']],
            headers='keys',
            tablefmt='fancy_grid',
            showindex=False
            ))
            
            cari = input("\nMasukkan Tanggal yang ingin dicari (atau tekan Enter untuk kembali): ").strip().lower()

            if not cari:
                print("\nKembali ke menu admin...")
                return

            hasil_index = binary_search(self.data.Date , cari)

            if hasil_index != -1:
                hasil = data.loc[hasil_index].copy()
                print("\nData transaksi yang ditemukan:")
                print(tabulate(
                    hasil.loc[hasil['Nama']==self.user['Nama'].copy().values[0], ['TransactionID', 'Date', 'Material', 'Nama', 'Quantity', 'Delivery', 'Subtotal']],
                    headers='keys',
                    tablefmt='fancy_grid',
                    showindex=False
                ))
            else:
                print(f"\nTidak ada transaksi yang ditemukan pada tanggal {cari}.")

            input("\nTekan Enter untuk kembali ke menu admin...")

    def CreateNewTransaction(self, cart):
        delivery = CalculateShippingCost(self.graph, KECAMATAN.lower(), self.user.Kecamatan.values[0].lower())[0] *10000
        total = sum(cart['Subtotal'].values) + delivery
        vTotal = sum(cart['SubVolume'].values)
        
        self.data.loc[len(self.data)] = [
                1 if self.data.empty else self.data.loc[len(self.data)-1, 'ID'] + 1,
                datetime.today().date(),
                self.user.loc[:, 'ID'].values[0],
                delivery,
                total,
                vTotal
            ]
        
        print(f'\n Transaksi anda dengan jumlah Rp {total} berhasil diproses')

        self.detail = pd.concat([self.detail, cart], axis=0, ignore_index=True)

        cart['ID'] = cart['ID'].astype(int)
        cart['TransactionID'] = cart['TransactionID'].astype('Int64')
        cart['MaterialID'] = cart['MaterialID'].astype('Int64')
        cart['Quantity'] = cart['Quantity'].astype('Int64')
        cart['Subtotal'] = cart['Subtotal'].astype('Int64')
        cart['SubVolume'] = cart['SubVolume'].astype(float)

        self.data.to_csv(TRANSACTION_FILE, index=False)
        self.detail.to_csv(DETAIL_FILE, index=False)
        self.material.to_csv(MATERIAL_FILE, index=False)

    def CreateTransactionMenu(self):
        loop = True
        cart = pd.DataFrame(columns=['ID', 'TransactionID','MaterialID', 'Quantity', 'Subtotal', 'SubVolume'])
        while loop:
            clear_terminal()
            
            print(tabulate(self.material, headers='keys', tablefmt='fancy_grid', showindex=False))
            
            materialId = Input('ID Material', 'num', True)

            if not isinstance(materialId, int) and not materialId.split():
                print('Kembali ke menu utama...')
                time.sleep(1)
                return

            material = self.material.loc[self.material.ID == materialId]

            if not materialId in self.material.ID.values:
                print('ID tidak terdaftar')
                time.sleep(2)
                continue
            
            quantity = Input('Jumlah', 'num')

            if quantity <= 0 :
                print('Jumlah dibeli harus lebih dari 0')
            
            if material.Stock.values[0] < quantity or material.Stock.values[0] == 0:
                print('Stock tidak mencukupi')
                time.sleep(2)
                continue
            
            subtotal = int(material.Price.values[0]) * int(quantity)
            subvolume = float(material.Volume.values[0] * quantity)

            self.material.loc[self.material.ID == materialId, 'Stock'] = int(material.Stock.values[0] - quantity)

            cart.loc[len(cart)] = [
                1 if self.detail.empty and cart.empty\
                    else (self.detail.loc[len(self.detail)-1, 'ID']) + 1 if cart.empty\
                        else int(cart.loc[len(cart)-1, 'ID']),
                        1 if self.data.empty else int(self.data.loc[len(self.data)-1, 'ID'] + 1),
                        int(materialId),
                        int(quantity),
                        int(subtotal),
                        float(subvolume)
            ]

            print(f"[{self.material.loc[self.material['ID']==materialId, 'Material'].values[0]}] sejumlah {quantity} telah ditambahkan ke keranjang")

            buy = Input('Ada material lain yang ingin dibeli? [Y/n]')

            while True:
                if buy.lower() == 'n':
                    loop = False
                    break
                elif buy.lower() == 'y':
                    break
                else:
                    print('Pilihan tidak valid!')
                    time.sleep(2)
                    ClearPrevLine(2)

        self.CreateNewTransaction(cart)

        print(f"Transaksi berhasil! Mohon tunggu barang dikirim")
        input('Tekan Enter untuk Melanjutkan')
        clear_terminal()