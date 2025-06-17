import csv
import pandas as pd
from tabulate import tabulate
import os

def kelola_angkutan():
    print("\n=== Kelola Angkutan dan Optimasi Pengiriman ===")

    # Load data truk
    def load_trucks():
        trucks = {}
        with open("dataAngkutan.csv", mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                truck_id = int(row["IDTruck"])
                trucks[truck_id] = {
                    "nama": row["Nama"],
                    "nopol": row["NoPolisi"],
                    "kapasitas": int(row["Kapasitas"])
                }
        return trucks

    # Load material
    def load_materials():
        materials = {}
        with open("material_dummy.csv", mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                material_id = int(row["ID"])
                materials[material_id] = {
                    "name": row["Material"],
                    "volume": float(row["Volume"])
                }
        return materials

    # Load transaksi dan hitung total volume
    def load_transaction_weights(materials):
        items = []
        with open("transaction.csv", mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
        for row in reader:
            try:
                mat_id = int(float(row["MaterialID"]))
                quantity = int(float(row["Quantity"]))
            except ValueError:
                print(f"Data transaksi tidak valid: {row}")
                continue  # ← harus di dalam except!

            if mat_id in materials:
                volume = materials[mat_id]["volume"]
                total_volume = quantity * volume
                items.append({
                    "name": materials[mat_id]["name"],
                    "value": total_volume,
                    "weight": volume
                })
        return items


    def unbounded_knapsack(items, capacity):
        dp = [0.0] * (capacity + 1)
        included = [[] for _ in range(capacity + 1)]
        for w in range(capacity + 1):
            for item in items:
                weight = int(item["weight"])
                if weight <= w:
                    if item["value"] + dp[w - weight] > dp[w]:
                        dp[w] = item["value"] + dp[w - weight]
                        included[w] = included[w - weight] + [item["name"]]
        return dp[capacity], included[capacity]

    # --- Eksekusi ---
    trucks = load_trucks()
    materials = load_materials()
    items = load_transaction_weights(materials)

    # Hitung total volume dari semua transaksi
    total_volume_transaksi = sum(item["value"] for item in items)

    print("\n=== Daftar Truk yang Tersedia ===")
    print(f"{'ID':<5} {'Nama':<20} {'Nopol':<15} {'Kapasitas (m³)':<15}")
    print("-" * 60)
    for tid, truck in trucks.items():
        print(f"{tid:<5} {truck['nama']:<20} {truck['nopol']:<15} {truck['kapasitas']:<15}")

    print(f"\n📦 Total volume transaksi yang perlu diangkut: {total_volume_transaksi:.2f} m³")

    # Input pemilihan truk
    selected = int(input("\nMasukkan ID truk yang ingin digunakan: "))
    capacity = trucks[selected]["kapasitas"]

    # Jalankan knapsack
    max_val, selected_items = unbounded_knapsack(items, capacity)

    print(f"\n✅ Total volume termuat: {max_val:.2f} m³ dari kapasitas {capacity} m³")
    print("📋 Barang yang dimuat:")
    for item in selected_items:
        print(f"- {item}")

