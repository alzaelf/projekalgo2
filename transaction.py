import os, sys, time
import pandas as pd
from tabulate import tabulate 
import json

TRANSACTION_FILE = 'transaction.csv'
MATERIAL_FILE = 'material_dummy.csv'
KECAMATAN = 'sumbersari'

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

# Dari source kode.py
def Check(inputs, type):
    try:
        if not inputs.strip():
            raise ValueError("Tidak boleh kosong")
        elif type == 'str' and inputs.isdigit():
            raise ValueError("Harus berupa huruf")
        elif type == 'num' and not inputs.isdigit() :
            raise ValueError("Harus berupa angka")
        
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

def Input(text, type = 'str'):
    while True:
        temp = input(f'{text} : ')
        if not Check(temp, type):
            time.sleep(2)
            ClearPrevLine(2)
            continue

        return temp if type == 'str' else int(temp)

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
        try:
            self.data = pd.read_csv(TRANSACTION_FILE)
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=['ID', 'MaterialID', 'UserID', 'Quantity', 'Delivery', 'Total'])
            self.data['Total'] = self.data['Total'].astype('int64')

        self.material = pd.read_csv(MATERIAL_FILE)

        user = pd.read_csv('user.csv')
        self.user = user.loc[user['ID'] == userId]

        self.graph = load_graph('kecamatan_graph.json')
        self.isAdmin = True if self.user.loc[:, 'Role'].values[0] == 'admin' else False

    def ShowAllTransaction(self):
        data = self.data.copy()

        # Mapping MaterialID ke Nama Material
        material_dict = dict(zip(self.material['ID'], self.material['Material']))
        data['Material'] = data['MaterialID'].map(material_dict)

        # Mapping UserID ke Nama User
        user_df = pd.read_csv('user.csv')
        user_dict = dict(zip(user_df['ID'], user_df['Nama']))
        data['User'] = data['UserID'].map(user_dict)

        # Ubah semua nama material ke huruf kecil untuk pencarian
        data['MaterialLower'] = data['Material'].str.lower()

        # Urutkan berdasarkan nama material (syarat binary search)
        data = data.sort_values(by='MaterialLower').reset_index(drop=True)
        daftar_material = data['MaterialLower'].tolist()

        # Tampilkan semua transaksi
        print(tabulate(
            data[['ID', 'Material', 'User', 'Quantity', 'Delivery', 'Total']],
            headers='keys',
            tablefmt='fancy_grid',
            floatfmt='.0f',
            showindex=False
        ))

        # Input pencarian material (dengan opsi kembali)
        cari = input("\nMasukkan nama Material yang ingin dicari (atau tekan Enter untuk kembali): ").strip().lower()

        if not cari:
            print("\nKembali ke menu admin...")
            return

        hasil_index = binary_search(daftar_material, cari)

        if hasil_index != -1:
            hasil = data.iloc[hasil_index]
            print("\nData transaksi yang ditemukan:")
            print(tabulate(
                hasil[['ID', 'Material', 'User', 'Quantity', 'Delivery', 'Total']],
                headers='keys',
                tablefmt='fancy_grid',
                showindex=False
            ))
        else:
            print("\nMaterial yang kamu cari tidak ditemukan.")

        input("\nTekan Enter untuk kembali ke menu admin...")


    def SearchDeliveryRoute(self, graph): # Pencarian Rute Pengiriman (Prims)
        mst = []
        vertices = set(graph.keys())
        visited = set()
        start_vertex = list(vertices)[0]

        visited.add(start_vertex)

        while len(visited) < len(vertices):
            min_edge = None
            min_weight = float('inf')

            for vertex in visited:
                for neighbor, weight in graph[vertex]:
                    if neighbor not in visited and weight < min_weight:
                        min_edge = (vertex, neighbor)
                        min_weight = weight

            if min_edge:
                mst.append((min_edge[0], min_edge[1], min_weight))
                visited.add(min_edge[1])

        return mst
    
    def CalculateShippingCost(self, start, finish): # Kalkulasi Ongkir (Djikstra)
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        predecessors = {node: None for node in self.graph}
        unvisited = set(self.graph.keys())
        
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
            
            for neighbor, weight in self.graph[current].items():
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

    def CreateNewTransaction(self, materialId, quantity, delivery, total):
        self.data.loc[len(self.data)] = [
                1 if self.data.empty else self.data.loc[len(self.data)-1, 'ID'] + 1,
                materialId,
                self.user.loc[:, 'ID'].values[0].astype(int),
                quantity,
                delivery,
                total
            ]

        self.data.to_csv(TRANSACTION_FILE, index=False)
        self.material.to_csv(MATERIAL_FILE, index=False)

    def CreateTransactionMenu(self):
        loop = True
        while loop:
            clear_terminal()
            
            print(tabulate(self.material, headers='keys', tablefmt='fancy_grid', showindex=False))
            
            materialId = Input('ID Material', 'num')

            if self.material.loc[self.material.ID == materialId].empty:
                print('ID tidak terdaftar')

                time.sleep(2)
                continue
            
            stock = self.material.loc[self.material.ID == materialId, 'Stock'].values[0]
            
            quantity = Input('Jumlah', 'num')
            
            if stock < quantity or stock == 0:
                print('Stock tidak mencukupi')
                time.sleep(2)
                
                continue
            
            kecamatan = self.user.loc[:, 'Kecamatan'].values[0].lower()

            delivery = self.CalculateShippingCost(KECAMATAN.lower(), kecamatan)[0] * 100
            materialPrice = self.material.loc[self.material.ID == materialId, 'Price'].values[0].astype(int)
            total = delivery + materialPrice * quantity
            
            self.material.loc[self.material.ID == materialId, 'Stock'] = stock - quantity

            self.CreateNewTransaction(materialId, quantity, delivery, total)

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



        print(f"Transaksi berhasil! Mohon tunggu barang dikirim")
        input('Tekan Enter untuk Melanjutkan')
        clear_terminal()