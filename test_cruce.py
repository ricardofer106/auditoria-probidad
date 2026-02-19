import pandas as pd
import requests
import time
import random

# Función de búsqueda (copiada de app.py para prueba)
def consultar_mercado_publico(rut_original):
    try:
        # Limpieza básica del RUT
        rut = str(rut_original).replace(".", "").replace("-", "").upper().strip()
        if len(rut) < 2: return False
        
        cuerpo, dv = rut[:-1], rut[-1]
        rut_formateado = "{:,}".format(int(cuerpo)).replace(",", ".") + "-" + dv
        
        url = f"https://www.mercadopublico.cl/Portal/V2/BusquedaProveedores?rut={rut_formateado}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}

        print(f"Consultando RUT: {rut_formateado}...", end=" ")
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if 'lblRazonSocial' in response.text and "No se encontraron proveedores" not in response.text:
            print("✅ ES PROVEEDOR")
            return True
        else:
            print("❌ No es proveedor (o no encontrado)")
            return False
            
    except Exception as e:
        print(f"⚠️ Error consultando: {e}")
        return False

# Cargar datos
try:
    print("Cargando archivo 'declaraciones_reales.csv'...")
    df = pd.read_csv("declaraciones_reales.csv", encoding='latin-1', sep=None, engine='python')
    print(f"Archivo cargado con {len(df)} registros.\n")

    # Iterar y probar
    for i, row in df.head(5).iterrows(): # Probamos solo los primeros 5 para rapidez
        rut = row.get('RUT Declarante', '')
        nombre = row.get('Nombre', 'Desconocido')
        
        print(f"[{i+1}/{len(df)}] {nombre}")
        consultar_mercado_publico(rut)
        
        # Pausa pequeña para simular el comportamiento real
        time.sleep(1) 
        print("-" * 30)

except FileNotFoundError:
    print("Error: No se encontró el archivo 'declaraciones_reales.csv'")
except Exception as e:
    print(f"Error inesperado: {e}")
