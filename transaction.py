import os
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
        elif type == 'num' and inputs.isalpha() :
            raise ValueError("Harus berupa angka")
        
        return inputs
    
    except ValueError as e:
        print(e)
        return False

def Input(text, type = 'str'):
    while True:
        temp = input(f'{text} : ')
        if not Check(temp, type): continue

        return temp if type == 'str' else int(temp)

class Material:
    def __init__(self, role):
        try:
            self.data = pd.read_csv(MATERIAL_FILE)
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=['ID', 'Material', 'Price', 'Stock', 'Volume'])
        
        self.isAdmin = True if role == 'admin' else False

    def AddMaterial(self):
        if self.isAdmin:
            print("Ini tambah material")
            
            while True:
                materialName = Input('Nama Material')

                if not self.data.loc[self.data.Material == materialName].empty:
                    print('Material sudah ada!')
                    continue
                break

            materialPrice = Input('Harga Material', 'num')
            materialStock = Input('Stok Material', 'num')
            materialVolume = Input('Volume Material', 'num')

            self.data.loc[len(self.data)] = [
                1 if self.data.empty else self.data.loc[len(self.data) - 1, 'ID'] + 1,
                materialName,
                materialPrice,
                materialStock,
                materialVolume
            ]

            self.data.to_csv(MATERIAL_FILE, index=False)

            print(f"{materialName} berhasil ditambahkan!")
            input('Tekan Enter untuk Melanjutkan')
            clear_terminal()
        
    def UpdateMaterial(self):
        if self.isAdmin:
            print('Ini daftar material')

            while True:
                materialId = Input('Material ID', 'num')
                
                if self.data.loc[self.data.ID == materialId].empty:
                    print('Material tidak ditemukan!')
                    continue
                break
            
            while True:
                materialName = Input('Nama Material')

                if not self.data.loc[self.data.Material == materialName].empty:
                    print('Material sudah ada!')
                    continue
                break

            materialPrice = Input('Harga Material', 'num')
            materialVolume = Input('Volume Material', 'num')

            self.data.loc[self.data.ID == materialId] =[
                materialId,
                materialName,
                materialPrice,
                materialVolume
            ]
            
            self.data.to_csv(MATERIAL_FILE, index=False)

            print(f"{materialName} berhasil ditambahkan!")
            input('Tekan Enter untuk Melanjutkan')
            clear_terminal()

    def ShowMaterial(self):
        print('Data tidak ditemukan' if self.data.empty
               else self.data.to_string(index=False))
        
        input('Tekan Enter Untuk Keluar')
        clear_terminal()

class Transaction:
    def __init__(self, userId):
        try:
            self.data = pd.read_csv(TRANSACTION_FILE)
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=['ID', 'MaterialID', 'UserID', 'Quantity', 'Delivery', 'Total'])

        self.material = pd.read_csv(MATERIAL_FILE)

        user = pd.read_csv('user.csv')
        self.user = user.loc[user['ID'] == userId]

        self.graph = load_graph('kecamatan_graph.json')
        self.isAdmin = True if self.user.loc[:, 'Role'].values[0] == 'admin' else False

    def ShowAllTransaction(self):
        if self.isAdmin:
            print(tabulate(self.data, headers='keys', tablefmt='fancy_grid', showindex=False))

        else:
            print(tabulate(
                self.data.loc[
                    self.data.UserID == self.user.loc[:, 'ID'].values[0],
                    ['ID', 'MaterialID', 'Quantity', 'Delivery', 'Total']], 
                headers='keys',
                tablefmt='fancy_grid',
                showindex=False
                ))
            
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

    def CreateTransaction(self):
        print('Ini List Material //Belum masuk material')
        materialId = Input('ID Material', 'num')
        quantity = Input('Jumlah', 'num')

        kecamatan = self.user.loc[:, 'Kecamatan'].values[0].lower()

        delivery = self.CalculateShippingCost(KECAMATAN.lower(), kecamatan)[0] * 100
        materialPrice = self.material.loc[self.material.ID == materialId, 'Price'].values[0].astype(int)
        total = delivery + materialPrice * quantity

        self.data.loc[len(self.data)] = [
            1 if self.data.empty else self.data.loc[len(self.data)-1, 'ID'] + 1,
            materialId,
            self.user.loc[:, 'ID'].values[0].astype(int),
            quantity,
            delivery,
            total
        ]

        self.data.to_csv(TRANSACTION_FILE, index=False)

        print(f"Transaksi berhasil! Mohon tunggu barang dikirim")
        input('Tekan Enter untuk Melanjutkan')
        clear_terminal()

    # Belum selesai
    def DeleteATransaction(self):
        transactionId = input("ID Transaksi : ")

        if not self.data.loc[self.data.ID == transactionId].empty:
            self.data.drop()