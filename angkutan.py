import csv
import pandas as pd
from tabulate import tabulate
import os

def kelola_angkutan():

    # Load data truk
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


    # Load material
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


    def load_transaction_weights(materials):
        try:
            df = pd.read_csv("transaction.csv")

            if df.empty:
                print("File transaction.csv kosong.")
                return []

            try:
                # Input ID Transaksi
                trx_id = int(input("Masukkan ID Transaksi yang ingin diproses: "))

                # Filter transaksi berdasarkan ID
                row = df[df["ID"] == trx_id]

                if row.empty:
                    print(f"Transaksi dengan ID {trx_id} tidak ditemukan.")
                    return []

                row = row.iloc[0]  # Ambil baris pertama dari hasil filter

                mat_id = int(float(row["MaterialID"]))
                quantity = int(float(row["Quantity"]))

                items = []

                if mat_id in materials:
                    volume = materials[mat_id]["volume"]
                    total_volume = quantity * volume

                    items.append({
                        "name": materials[mat_id]["name"],
                        "value": total_volume,
                        "weight": volume
                    })
                else:
                    print(f"Material ID {mat_id} tidak ditemukan dalam data 'materials'.")

                return items

            except ValueError as e:
                print(f"Input tidak valid. Error: {e}")
                return []

        except FileNotFoundError:
            print("File transaction.csv tidak ditemukan.")
            return []

        except Exception as e:
            print(f"Error membaca file transaction.csv: {e}")
            return []


    def unbounded_knapsack(items, capacity):
        if not items:
            return 0.0, []

        max_volume = 0.0
        best_combination = []

        def backtrack(used, total_volume):
            nonlocal max_volume, best_combination
            if total_volume > capacity:
                return
            if total_volume > max_volume:
                max_volume = total_volume
                best_combination = used[:]
            for item in items:
                used.append(item["name"])
                backtrack(used, total_volume + item["weight"])
                used.pop()

        backtrack([], 0.0)
        return max_volume, best_combination
    
    trucks = load_trucks()
    if not trucks:
        print("Tidak ada data truk yang tersedia.")
        return

    materials = load_materials()
    if not materials:
        print("Tidak ada data material yang tersedia.")
        return

    items = load_transaction_weights(materials)
    if not items:
        print("Tidak ada data transaksi yang tersedia.")
        return

    total_volume_transaksi = sum(item["value"] for item in items)

    trucks_df = pd.DataFrame([
    {"ID": tid, "Nama": t["nama"], "Nopol": t["nopol"], "Kapasitas (m³)": t["kapasitas"]}
    for tid, t in trucks.items()
    ])

    print("\n=== Daftar Truk yang Tersedia ===")
    print(tabulate(trucks_df, headers="keys", tablefmt="fancy_grid", showindex=False))

    print(f"\n Total volume transaksi yang perlu diangkut: {total_volume_transaksi:.2f} m³")

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

    # Jalankan knapsack
    max_val, selected_items = unbounded_knapsack(items, capacity)

    print(f"\nTruk terpilih: {trucks[selected]['nama']} ({trucks[selected]['nopol']})")
    print(f"Total volume termuat: {max_val:.2f} m³ dari kapasitas {capacity} m³")
    print(f"Efisiensi pemuatan: {(max_val/capacity)*100:.1f}%")
    
    if selected_items:
        print("\n Barang yang dimuat:")
        for item in selected_items:
            print(f"- {item}")
    else:
        print("\nTidak ada barang yang bisa dimuat.")

    input("\nTekan Enter untuk kembali ke menu...")