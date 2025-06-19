from transaction import MATERIAL_FILE, Input, clear_terminal, ClearPrevLine
import pandas as pd
from tabulate import tabulate
import time

def UbahMaterial():
    try:
        data = pd.read_csv(MATERIAL_FILE)
    except FileNotFoundError:
        data = pd.DataFrame(columns=['ID', 'Material', 'Price', 'Stock', 'Volume'])

    if data.empty:
        print("Tidak ada material yang terdaftar")
        input('Tekan Enter untuk kembali...')
        return

    print(tabulate(data, headers='keys', tablefmt='fancy_grid',showindex=False))

    while True:
        materialId = Input('Material ID', 'num', null=True)
        if not isinstance(materialId, int) and not materialId.split():
            input('Tekan enter untuk kembali...')
            clear_terminal()
            return

        if not materialId in data.ID.values:
            print(f'Material dengan ID : {materialId} tidak ada dalam database')
            time.sleep(2)
            ClearPrevLine(2)
            continue
        break
    
    material = data.loc[data.ID == materialId]

    while True:
        materialName = Input(f'Nama Material [{material.Material.values[0]}]', null=True)

        if not materialName.split():
            materialName = material.Material.values[0]
            break

        if materialName in data.Material.values:
            print('Material sudah ada dalam database')
            time.sleep(2)
            ClearPrevLine(2)
            continue
        break

    while True:
        priceMaterial = Input(f'Harga [{material.Price.values[0]}]', 'num', null=True)
        if not isinstance(priceMaterial, int) and not priceMaterial.split():
            priceMaterial = material.Price.values[0]
            break

        if priceMaterial < 0:
            print('Harga material harus bilangan bulat positif')
            time.sleep(2)
            ClearPrevLine(2)
            continue
        break

    while True:
        stockMaterial = Input(f'Jumlah stok [{material.Stock.values[0]}]', 'num', null=True)
        if not isinstance(stockMaterial, int) and not stockMaterial.split():
            stockMaterial = material.Stock.values[0]
            break
        if stockMaterial < 0:
            print('Stok material harus bilangan bulat positif')
            time.sleep(2)
            ClearPrevLine(2)
            continue
        break

    while True:
        volumeMaterial = Input(f'Volume [{material.Volume.values[0]}]', 'flo', null=True)
        if not isinstance(volumeMaterial, float) and not volumeMaterial.split():
            volumeMaterial = material.Volume.values[0]
            break
        if volumeMaterial < 0:
            print('Volume material harus berupa bilangan ril positif')
            time.sleep(2)
            ClearPrevLine(2)
            continue
        break

    print(volumeMaterial)

    data.loc[data.ID == materialId] = [materialId, materialName, priceMaterial, stockMaterial, volumeMaterial]

    data.to_csv('material_dummy.csv', index=False)

    print(tabulate(data, headers='keys', tablefmt='fancy_grid', showindex=False))