import csv
import pandas as pd
from tabulate import tabulate
from transaction import KECAMATAN, load_graph, CalculateShippingCost

def GrafMST(kecamatan = list):
    graf = load_graph('kecamatan_graph.json')

    hasil = {v:[] for v in kecamatan}
    rute = {v:{} for v in kecamatan}

    for i in hasil:
        for j in kecamatan:
            if i == j:
                continue

            hasil[i].append((j, CalculateShippingCost(graf, i, j)[0]))
            rute[i][j] = CalculateShippingCost(graf, i, j)[1]
            # hasil[i][j] = CalculateShippingCost(graf, i, j)[0]
    
    return hasil

def RuteAngkutan(graph): # Pencarian Rute Pengiriman (Prims)
    mst = []
    vertices = graph.keys()
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

def graf_teks(graph):
    adj = {}
    for u, v, w in graph:
        if u not in adj:
            adj[u] = []
        if v not in adj:
            adj[v] = []
        adj[u].append((v, w))
        adj[v].append((u, w))
    
    lines = []
    visited_edges = set()
    
    # mencari kecamatan dengan tetangga lebih dari 1
    center = None
    for node, neighbors in adj.items():
        if len(neighbors) > 1:
            center = node
            break
    
    # jika terdapat kecamatan dengan tetangga lebih dari 1
    if center:
        for v, w in adj[center]:
            edge = tuple(sorted([center, v]))
            if edge not in visited_edges:
                if len(adj[v]) > 1:
                    for v2, w2 in adj[v]:
                        if v2 != center:
                            lines.append(f"{center} --({w:.1f})--> {v} --({w2:.1f})--> {v2}")
                            visited_edges.add(tuple(sorted([v, v2])))
                            break
                else:
                    lines.append(f"{center} --({w:.1f})--> {v}")
                visited_edges.add(edge)

    # jika tidak ada kecamatan dengan tetangga lebih dari 1
    else:
        start = None
        for node, neighbors in adj.items():
            if len(neighbors) == 1:
                start = node
                break
        
        current = start
        line = []
        while current:
            line.append(current)
            next_node = None
            for neighbor, weight in adj[current]:
                if tuple(sorted([current, neighbor])) not in visited_edges:
                    line.append(f"--({weight:.1f})-->")
                    visited_edges.add(tuple(sorted([current, neighbor])))
                    next_node = neighbor
                    break
            current = next_node
        lines.append(" ".join(str(x) for x in line))
    
    return "\n".join(lines)

def kelola_angkutan():

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

    try:
        trx_df = pd.read_csv("transaction.csv")
        trx_df_display = trx_df[["ID", "Date", "UserID", "Delivery", "VTotal"]]
        print("\n=== Daftar Transaksi yang Tersedia ===")
        print(tabulate(trx_df_display, headers="keys", tablefmt="grid", showindex=False))
    except Exception as e:
        print(f"Gagal membaca transaksi: {e}")
        return

    try:
        selected_ids = input("\nMasukkan ID transaksi yang ingin diproses (pisahkan dengan koma): ")
        selected_ids = [int(i.strip()) for i in selected_ids.split(",") if i.strip().isdigit()]
        if not selected_ids:
            print("Tidak ada ID transaksi yang valid.")
            return
    except Exception as e:
        print(f"Input tidak valid: {e}")
        return

    def load_transactions_and_details(materials, selected_ids):
        try:
            trx_df = pd.read_csv("transaction.csv")
            detail_df = pd.read_csv("detail_transaction.csv")
            kecamatan_df = pd.read_csv("kecamatan.csv")

            trx_df = trx_df[trx_df["ID"].isin(selected_ids)]
            detail_df = detail_df[detail_df["TransactionID"].isin(selected_ids)]

            merged = pd.merge(detail_df, trx_df, left_on="TransactionID", right_on="ID", suffixes=("_detail", "_trx"))

            items = []
            tujuan = set()
            total_volume_calculated = 0  
            
            for _, row in merged.iterrows():
                mat_id = int(float(row["MaterialID"]))
                quantity = int(float(row["Quantity"]))
                kecamatan_id = int(row["Delivery"])
                tujuan.add(kecamatan_id)
                if mat_id in materials:
                    volume = materials[mat_id]["volume"]
                    total_volume_calculated += volume * quantity  
                    items.append({
                        "name": materials[mat_id]["name"],
                        "value": volume,
                        "weight": volume,
                        "max_quantity": quantity,
                        "kecamatan_id": kecamatan_id
                    })

            tujuan_nama = []
            for kid in tujuan:
                nama = kecamatan_df[kecamatan_df["ID"] == kid]["Kecamatan"]
                if not nama.empty:
                    tujuan_nama.append(nama.values[0])
                else:
                    tujuan_nama.append(f"ID_{kid} (tidak ditemukan)")
            
            return items, tujuan_nama, total_volume_calculated  
        except Exception as e:
            print(f"Error load transaksi: {e}")
            return [], [], 0

    def bounded_knapsack(items, capacity):
        
        selected_items = []
        total_weight = 0
        total_value = 0
        
        for item in items:
            quantity = int(item["max_quantity"])
            weight_per_unit = item["weight"]
            value_per_unit = item["value"]
            
            
            selected_items.extend([item["name"]] * quantity)
            total_weight += weight_per_unit * quantity
            total_value += value_per_unit * quantity
        
        return total_value, selected_items

    trucks = load_trucks()
    if not trucks:
        print("Tidak ada data truk yang tersedia.")
        return

    materials = load_materials()
    if not materials:
        print("Tidak ada data material yang tersedia.")
        return

    items, tujuan_nama, total_volume_transaksi = load_transactions_and_details(materials, selected_ids)
    if not items:
        print("Tidak ada data transaksi yang tersedia.")
        return

    print("\n=== DEBUG: Detail Items ===")
    for item in items:
        print(f"- {item['name']}: {item['max_quantity']} unit × {item['value']:.3f} m³ = {item['value'] * item['max_quantity']:.3f} m³")
    print(f"Total volume calculated: {sum(item['value'] * item['max_quantity'] for item in items):.3f} m³")
    print("==============================")

    trucks_df = pd.DataFrame([
        {"ID": tid, "Nama": t["nama"], "Nopol": t["nopol"], "Kapasitas (m³)": t["kapasitas"]}
        for tid, t in trucks.items()
    ])

    print("\n=== Daftar Truk yang Tersedia ===")
    print(tabulate(trucks_df, headers="keys", tablefmt="fancy_grid", showindex=False))

    print(f"\nTotal volume seluruh transaksi: {total_volume_transaksi:.2f} m³")
    print(f"Daftar kecamatan tujuan: {', '.join(tujuan_nama)}")

    # Input pemilihan truk dengan validasi
    try:
        selected = int(input("\nMasukkan ID truk yang ingin digunakan: "))
        if selected not in trucks:
            print("ID truk tidak ditemukan.")
            return
    except ValueError:
        print("Input harus berupa angka.")
        return
    except KeyboardInterrupt:
        print("\n Operasi dibatalkan.")
        return

    capacity = trucks[selected]["kapasitas"]

    # Jalankan bounded knapsack
    max_val, selected_items = bounded_knapsack(items, capacity)

    print(f"\nTruk terpilih: {trucks[selected]['nama']} ({trucks[selected]['nopol']})")
    print(f"Total volume termuat: {max_val:.2f} m³ dari kapasitas {capacity} m³")
    print(f"Efisiensi pemuatan: {(max_val/capacity)*100:.1f}%")

    if selected_items:
        print("\nBarang yang dimuat:")
        for item in set(selected_items):
            print(f"- {item}: {selected_items.count(item)}")
    else:
        print("\nTidak ada barang yang bisa dimuat.")

    print(f"\nTruk akan berhenti di kecamatan: {', '.join(tujuan_nama)}")
    
    # implementasi MST

    
    rute = [KECAMATAN] + [tujuan.lower() for tujuan in tujuan_nama]

    graf = GrafMST(rute)

    print('Dengan Rute:')

    print(graf_teks(RuteAngkutan(graf)))

    input("\nTekan Enter untuk kembali ke menu...")