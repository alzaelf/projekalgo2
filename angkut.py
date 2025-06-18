import pandas as pd
from tabulate import tabulate
from transaction import load_graph, GetCsv

GRAPH = load_graph('kecamatan_graph.json')

KECAMATAN = 'sumbersari'
USER = GetCsv('user.csv')
TRANSACTION = GetCsv('transaction.csv')
DETAIL = GetCsv('detail_transaction.csv')

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

# def get_map(kecamatan = list):
#     maps = dict()

#     unvisited = set(USER['Kecamatan'].values)

#     maps = {v:{} for v in USER['Kecamatan'].values}
#     for map in maps:
#         if map
#         maps[map][map]

def build_map(vertice, graph):
    edges = []
    for i in range(len(vertice)):
        src = vertice[i]
        dist = CalculateShippingCost(graph, src)
        for j in range(i + 1, len(vertice)):
            dst = vertice[j]
            edges.append((dist[dst], src, dst))  # weight, from, to
    return edges

def make_map(vertice):
    edge = {v : {} for v in vertice}

    for v in vertice:
        for ver in vertice:
            edge[v][ver] = CalculateShippingCost(GRAPH, v, ver)

    return edge


def SearchDeliveryRoute(graph): # Pencarian Rute Pengiriman (Prims)
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

def load_trucks():
    try:
        df = pd.read_csv("dataAngkutan.csv")
        trucks = {}
        for _, row in df.iterrows():
            truck_id = int(row["IDTruck"])
            trucks[truck_id] = {
                "nama": row["Nama"],
                "nopol": row["NoPolisi"],
                "kapasitas": int(row["Kapasitas"])
            }
        return trucks
    except FileNotFoundError:
        print("File dataAngkutan.csv tidak ditemukan.")
        return {}
    except Exception as e:
        print(f"Error membaca file dataAngkutan.csv: {e}")
        return {}

def load_materials():
    try:
        df = pd.read_csv("material_dummy.csv")
        materials = {}
        for _, row in df.iterrows():
            material_id = int(row["ID"])
            materials[material_id] = {
                "name": row["Material"],
                "volume": float(row["Volume"])
            }
        return materials
    except FileNotFoundError:
        print("File material_dummy.csv tidak ditemukan.")
        return {}
    except Exception as e:
        print(f"Error membaca file material_dummy.csv: {e}")
        return {}

def load_transaction_items(materials):
    try:
        df_trans = pd.read_csv("transaction.csv")
        df_detail = pd.read_csv("detail_transaction.csv")

        if df_trans.empty or df_detail.empty:
            print("File transaksi kosong.")
            return []

        trx_input = input("Masukkan Kode Transaksi (pisahkan dengan koma, contoh: 1,2,3): ").strip()
        trx_ids = [tid.strip() for tid in trx_input.split(",") if tid.strip()]

        # Cek setiap ID
        missing = [tid for tid in trx_ids if tid not in df_trans['ID'].astype(str).values]
        if missing:
            print(f" Transaksi tidak ditemukan: {', '.join(missing)}")
            return []

        filtered = df_detail[df_detail['TransactionID'].astype(str).isin(trx_ids)]

        if filtered.empty:
            print("Tidak ada detail transaksi untuk ID tersebut.")
            return []

        temp= pd.merge(df_trans, USER[['ID', 'Kecamatan']], how='left')
        kec = [k for k in temp['Kecamatan'].values]

        # print(make_map(kec))

        items = []
        for _, row in filtered.iterrows():
            mat_id = int(row["MaterialID"])
            qty = int(row["Quantity"])

            if mat_id in materials:
                mat = materials[mat_id]
                items.append({
                    "name": f"{mat['name']} (Trx {row['TransactionID']})",
                    "weight": qty * mat["volume"],
                    "value": qty * mat["volume"]
                })
            else:
                print(f"Material ID {mat_id} tidak ditemukan.")

        return items
    except Exception as e:
        print(f"Error saat membaca transaksi: {e}")
        return []

def zero_one_knapsack(items, capacity, scale=10):
    # Skala untuk menangani float -> int
    capacity_scaled = int(capacity * scale)
    n = len(items)

    dp = [[0] * (capacity_scaled + 1) for _ in range(n + 1)]

    weights = [int(item['weight'] * scale) for item in items]
    values = [item['value'] for item in items]

    for i in range(1, n + 1):
        for w in range(capacity_scaled + 1):
            if weights[i - 1] <= w:
                dp[i][w] = max(
                    values[i - 1] + dp[i - 1][w - weights[i - 1]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack untuk mencari item yang dipilih
    w = capacity_scaled
    selected = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1])
            w -= weights[i - 1]

    total_weight = sum(i['weight'] for i in selected)
    return total_weight, selected[::-1]

def kelola_angkutan():
    trucks = load_trucks()
    if not trucks:
        print("Tidak ada data truk yang tersedia.")
        return

    materials = load_materials()
    if not materials:
        print("Tidak ada data material yang tersedia.")
        return

    items = load_transaction_items(materials)
    if not items:
        print("Tidak ada item untuk transaksi ini.")
        return

    total_volume_transaksi = sum(item["weight"] for item in items)

    trucks_df = pd.DataFrame([
        {"ID": tid, "Nama": t["nama"], "Nopol": t["nopol"], "Kapasitas (m)": t["kapasitas"]}
        for tid, t in trucks.items()
    ])

    print("\n=== Daftar Truk yang Tersedia ===")
    print(tabulate(trucks_df, headers="keys", tablefmt="grid", showindex=False))

    print(f"\n Total volume transaksi: {total_volume_transaksi:.2f} m3")

    try:
        selected = int(input("Masukkan ID truk yang ingin digunakan: "))
        if selected not in trucks:
            print("ID truk tidak ditemukan.")
            return
    except ValueError:
        print("Input harus berupa angka.")
        return

    capacity = trucks[selected]["kapasitas"]

    # Filter barang berukuran besar
    oversized = [item for item in items if item["weight"] > capacity]
    items = [item for item in items if item["weight"] <= capacity]

    max_val, selected_items = zero_one_knapsack(items, capacity, 1000)

    if oversized:
        print("\n Barang terlalu besar & tidak bisa dimuat ke truk:")
        for item in oversized:
            print(f"- {item['name']} ({item['weight']} m3 > kapasitas {capacity} m3)")


    print(f"\n Truk terpilih: {trucks[selected]['nama']} ({trucks[selected]['nopol']})")
    print(f" Volume termuat: {max_val:.2f} m3 dari {capacity} m3")
    print(f" Efisiensi muat: {(max_val / capacity * 100):.1f}%")

    if selected_items:
        print("\n Daftar barang terangkut:")
        for item in selected_items:
            print(f"- {item['name']} ({item['weight']} m3)")
    else:
        print("Tidak ada barang yang bisa dimuat.")

    input("\nTekan Enter untuk kembali ke menu...")
