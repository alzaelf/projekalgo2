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

    # Load data transaksi dan tampilkan
    try:
        trx_df = pd.read_csv("transaction.csv")
        trx_df_display = trx_df[["ID", "Date", "UserID", "Delivery", "VTotal"]]
        print("\n=== Daftar Transaksi yang Tersedia ===")
        print(tabulate(trx_df_display, headers="keys", tablefmt="grid", showindex=False))
    except Exception as e:
        print(f"Gagal membaca transaksi: {e}")
        return

    # Input ID transaksi yang dipilih
    try:
        selected_ids = input("\nMasukkan ID transaksi yang ingin diproses (pisahkan dengan koma): ")
        selected_ids = [int(i.strip()) for i in selected_ids.split(",") if i.strip().isdigit()]
        if not selected_ids:
            print("Tidak ada ID transaksi yang valid.")
            return
    except Exception as e:
        print(f"Input tidak valid: {e}")
        return

    # Load transaksi dan detail
    def load_transactions_and_details(materials, selected_ids):
        try:
            trx_df = pd.read_csv("transaction.csv")
            detail_df = pd.read_csv("detail_transaction.csv")
            kecamatan_df = pd.read_csv("kecamatan.csv")

            # Filter transaksi yang dipilih
            trx_df = trx_df[trx_df["ID"].isin(selected_ids)]
            detail_df = detail_df[detail_df["TransactionID"].isin(selected_ids)]

            # Gabungkan transaksi dan detail
            merged = pd.merge(detail_df, trx_df, left_on="TransactionID", right_on="ID", suffixes=("_detail", "_trx"))

            items = []
            tujuan = set()
            total_volume_calculated = 0  # Tambahkan variabel untuk menghitung total volume
            
            for _, row in merged.iterrows():
                mat_id = int(float(row["MaterialID"]))
                quantity = int(float(row["Quantity"]))
                kecamatan_id = int(row["Delivery"])
                tujuan.add(kecamatan_id)
                if mat_id in materials:
                    volume = materials[mat_id]["volume"]
                    total_volume_calculated += volume * quantity  # Hitung total volume
                    items.append({
                        "name": materials[mat_id]["name"],
                        "value": volume,
                        "weight": volume,
                        "max_quantity": quantity,
                        "kecamatan_id": kecamatan_id
                    })

            # Mapping kecamatan
            tujuan_nama = []
            for kid in tujuan:
                nama = kecamatan_df[kecamatan_df["ID"] == kid]["Kecamatan"]
                if not nama.empty:
                    tujuan_nama.append(nama.values[0])
                else:
                    tujuan_nama.append(f"ID_{kid} (tidak ditemukan)")
            
            return items, tujuan_nama, total_volume_calculated  # Return total volume yang dihitung
        except Exception as e:
            print(f"Error load transaksi: {e}")
            return [], [], 0

    def bounded_knapsack(items, capacity):
        """
        Ambil SEMUA barang sesuai quantity pesanan customer
        Tidak peduli apakah melebihi kapasitas truk atau tidak
        """
        selected_items = []
        total_weight = 0
        total_value = 0
        
        # Ambil SEMUA barang sesuai quantity yang dipesan
        for item in items:
            quantity = int(item["max_quantity"])
            weight_per_unit = item["weight"]
            value_per_unit = item["value"]
            
            # Tambahkan ke selected items
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

    # PERBAIKAN: Gunakan fungsi yang mengembalikan total volume yang konsisten
    items, tujuan_nama, total_volume_transaksi = load_transactions_and_details(materials, selected_ids)
    if not items:
        print("Tidak ada data transaksi yang tersedia.")
        return

    # DEBUG: Tampilkan informasi detail item
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

    input("\nTekan Enter untuk kembali ke menu...")