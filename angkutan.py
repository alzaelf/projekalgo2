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
    
    def format_koma(angka, presisi=3):
        return f"{angka:.{presisi}f}".replace('.', ',')

    def load_trucks():
        try:
            df = pd.read_csv("dataAngkutan.csv")
            return {
                int(row["IDTruck"]): {
                    "nama": row["Nama"],
                    "nopol": row["NoPolisi"],
                    "kapasitas": float(row["Kapasitas"])
                } for _, row in df.iterrows()
            }
        except Exception as e:
            print(f"Gagal membaca data truk: {e}")
            return {}

    def load_transaksi_vtotal():
        try:
            df = pd.read_csv("transaction.csv")
            return df[["ID", "UserID", "VTotal"]].dropna()
        except Exception as e:
            print(f"Gagal membaca data transaksi: {e}")
        return pd.DataFrame()


    def load_kecamatan():
        try:
            df = pd.read_csv("kecamatan.csv")
            return df.set_index("ID")["Kecamatan"].to_dict()
        except Exception as e:
            print(f"Gagal membaca data kecamatan: {e}")
            return {}
        
    def data_user():
        try:
            df = pd.read_csv("user.csv")
            return df.set_index("ID").to_dict(orient="index")
        except Exception as e:
            print(f"Gagal membaca data user: {e}")
            return {}
        
    def knapsack(transactions, capacity):
        scale = 1000
        cap = int(capacity * scale)
        n = len(transactions)

        weights = (transactions["VTotal"] * scale).astype(int).tolist()
        values = weights
        ids = transactions["ID"].tolist()

        dp = [[0] * (cap + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            for w in range(cap + 1):
                if weights[i - 1] <= w:
                    dp[i][w] = max(dp[i - 1][w],
                                   dp[i - 1][w - weights[i - 1]] + values[i - 1])
                else:
                    dp[i][w] = dp[i - 1][w]

        # Rekonstruksi solusi
        w = cap
        selected_indexes = []
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected_indexes.append(i - 1)
                w -= weights[i - 1]

        return transactions.iloc[selected_indexes], sum([transactions.iloc[i]["VTotal"] for i in selected_indexes])

    # Mulai proses
    trucks = load_trucks()
    if not trucks:
        print("Tidak ada data angkutan.")
        return

    print("\n=== Pilih Truk ===")
    print(tabulate([
        {"ID": tid, "Nama": t["nama"], "Nopol": t["nopol"], "Kapasitas (m³)": format_koma(t["kapasitas"])}
        for tid, t in trucks.items()
    ], headers="keys", tablefmt="fancy_grid", showindex=False))

    try:
        selected_id = int(input("\nMasukkan ID angkutan yang ingin digunakan: "))
        if selected_id not in trucks:
            print("ID angkutan tidak ditemukan.")
            return
    except:
        print("Input tidak valid.")
        return

    kapasitas = trucks[selected_id]["kapasitas"]
    print(f"\n Angkutan dipilih: {trucks[selected_id]['nama']} ({trucks[selected_id]['nopol']}), kapasitas {format_koma(kapasitas)} m³")

    transaksi_df = load_transaksi_vtotal()
    if transaksi_df.empty:
        print("Tidak ada data transaksi valid.")
        return

    kecamatan_dict = load_kecamatan()
    selected_trx, total_volume = knapsack(transaksi_df, kapasitas)

    if selected_trx.empty:
        print("\nTidak ada transaksi yang dapat dimuat.")
    else:
        user_data = data_user()
        
        trx_display = []
        tujuan_nama = []

        for _, row in selected_trx.iterrows():
            user_id = int(row["UserID"])
            user_info = user_data.get(user_id, {})
            nama_kec = user_info.get("Kecamatan", "Tidak Diketahui")

            trx_display.append({
                "ID": int(row["ID"]),
                "User": user_info.get("Nama", f"User {user_id}"),
                "Kecamatan": nama_kec,
                "VTotal (m³)": format_koma(row["VTotal"])
            })

            if nama_kec not in tujuan_nama:
                tujuan_nama.append(nama_kec)


        print("\n=== Transaksi Terpilih untuk Dimuat ===")
        print(tabulate(trx_display, headers="keys", tablefmt="fancy_grid", showindex=False))

        print(f"\n Total volume termuat: {format_koma(total_volume)} m³ dari kapasitas {format_koma(kapasitas)} m³")
        print(f" Efisiensi muatan: {format_koma(total_volume / kapasitas * 100, presisi=1)}%")

        print(f"\nTruk akan berhenti di kecamatan: {', '.join(tujuan_nama)}")

        rute = GrafMST([KECAMATAN] + [kec.lower() for kec in tujuan_nama])

        graf = GrafMST(rute)

        print('Dengan Rute:')

        print(graf_teks(RuteAngkutan(graf)))

        

    input("\nTekan Enter untuk kembali ke menu...")
