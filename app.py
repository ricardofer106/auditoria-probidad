import streamlit as st
import pandas as pd
import requests
import re
import time
import random
import io

# Configuración de página con tema verde
st.set_page_config(
    page_title="Auditoría de Probidad",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos personalizados para forzar color verde
st.markdown("""
    <style>
    /* Estilo general para el encabezado */
    h1 {color: #2e7d32 !important;}
    h2, h3 {color: #43a047 !important;}
    
    /* Botones primarios */
    .stButton>button {
        background-color: #4caf50 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #388e3c !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Botón de descarga específico */
    .stDownloadButton>button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* Éxito y alertas */
    .stSuccess {
        background-color: #e8f5e9 !important;
        color: #1b5e20 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Función de búsqueda
def consultar_mercado_publico(rut_original):
    try:
        rut = str(rut_original).replace(".", "").replace("-", "").upper().strip()
        if len(rut) < 2: return False
        cuerpo, dv = rut[:-1], rut[-1]
        try:
            rut_formateado = "{:,}".format(int(cuerpo)).replace(",", ".") + "-" + dv
        except ValueError:
            return False
        
        url = f"https://www.mercadopublico.cl/Portal/V2/BusquedaProveedores?rut={rut_formateado}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}

        response = requests.get(url, headers=headers, timeout=10)
        if 'lblRazonSocial' in response.text and "No se encontraron proveedores" not in response.text:
            return True
    except:
        pass
    return False

# --- Interfaz Web ---
st.title("✅ Portal de Auditoría de Probidad")
st.markdown("### Cruce de Datos de Intereses y Patrimonio con Mercado Público")
st.markdown("Sube tu archivo CSV para verificar si los funcionarios o sus relacionados figuran como proveedores del Estado.")

archivo = st.file_uploader("📂 Cargar archivo de declaraciones (CSV)", type=["csv"], help="El archivo debe contener una columna 'RUT Declarante'")

if archivo:
    try:
        # Intentamos detectar la codificación correcta
        try:
             df = pd.read_csv(archivo, encoding='utf-8', sep=None, engine='python')
        except:
             df = pd.read_csv(archivo, encoding='latin-1', sep=None, engine='python')

        st.success(f"✅ Archivo cargado exitosamente: {len(df)} registros encontrados.")
        
        # Normalización de Columnas (Busqueda Inteligente)
        cols_lower = {col.lower().strip(): col for col in df.columns}
        
        # Buscamos columnas clave con diversas variaciones
        def buscar_columna(keywords):
            for key, real_col in cols_lower.items():
                if any(k in key for k in keywords):
                    return real_col
            return None

        col_rut_declarante = buscar_columna(['rut declarante', 'rut_declarante'])
        col_rut_conyuge = buscar_columna(['rut cónyuge', 'rut conyuge', 'rut_conyuge', 'conyuge'])
        col_sociedades = buscar_columna(['sociedades', 'sociedad', 'participacion'])
        col_nombre_conyuge = buscar_columna(['nombre cónyuge', 'nombre conyuge'])

        # Validamos que al menos esté el RUT del declarante
        if not col_rut_declarante:
             st.error("❌ No se encontró la columna 'RUT Declarante'. Por favor verifica el archivo.")
        else:
            if st.button("🔍 Iniciar Auditoría Completa"):
                progreso = st.progress(0)
                status_text = st.empty()
                resultados = []
                
                with st.spinner('Realizando cruce de datos con Mercado Público...'):
                    for i, row in df.iterrows():
                        # Actualizar barra de progreso
                        progreso.progress((i + 1) / len(df))
                        
                        # Datos del Funcionario (Siempre buscamos esto primero)
                        rut_declarante = row.get(col_rut_declarante, '')
                        nombre_declarante = row.get('Nombre', 'Funcionario')
                        
                        # Variables de Hallazgos
                        hallazgo_encontrado = False
                        detalles = []
                        
                        status_text.text(f"Analizando [{i+1}/{len(df)}]: {rut_declarante}...")
                        
                        # --- 1. AUDITORÍA EXHAUSTIVA DE TODA LA FILA ---
                        # Buscamos RUTs en TODAS las columnas (incluyendo Hijos, Padres, Socios, etc.)
                        ruts_encontrados_fila = set()
                        
                        for col_nombre, val in row.items():
                            valor_str = str(val).strip()
                            # Regex para capturar RUTs: 1 o 2 dígitos, punto opcional, 3 dígitos, punto opcional, 3 dígitos, guión, dígito o K
                            # Ejemplos: 12.345.678-9, 12345678-9, 1.234.567-k
                            ruts_en_celda = re.findall(r'\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b', valor_str)
                            
                            for rut_detectado in ruts_en_celda:
                                # Normalizamos para evitar duplicados en la misma fila
                                rut_norm = rut_detectado.replace(".", "").replace("-", "").upper().strip()
                                if rut_norm in ruts_encontrados_fila: continue
                                ruts_encontrados_fila.add(rut_norm)
                                
                                # Consultamos Mercado Público
                                if consultar_mercado_publico(rut_detectado):
                                    hallazgo_encontrado = True
                                    es_declarante = (rut_detectado == rut_declarante)
                                    rol = "FUNCIONARIO" if es_declarante else f"RELACIONADO (en columna '{col_nombre}')"
                                    detalles.append(f"{rol} es proveedor ({rut_detectado})")

                        # --- 2. Validar Declaración de Sociedades (Texto) ---
                        sociedades = str(row.get(col_sociedades, '')).strip() if col_sociedades else ''
                        soc_lower = sociedades.lower()
                        if sociedades and soc_lower not in ['no posee', 'ninguna', 'nan', 'none', '', 'no aplica', 'sin informacion']:
                            hallazgo_encontrado = True
                            detalles.append(f"DECLARA SOCIEDADES: {sociedades}")

                        # Resultado Final
                        if hallazgo_encontrado:
                            resultado_texto = "CON OBSERVACIÓN"
                            st.warning(f"⚠️ **ALERTA en registro {i+1} ({nombre_declarante}):** {'; '.join(detalles)}")
                        else:
                            resultado_texto = "SIN HALLAZGOS"

                        resultados.append(resultado_texto)
                        # (Omitimos guardar detalles en el Excel como se solicitó)
                        
                        time.sleep(random.uniform(0.5, 1.5)) # Pausa para evitar bloqueos

                # df['Estado'] = resultados
                status_text.markdown("**✅ Auditoría completada.**")
                st.balloons()
                
                # Preparar descarga Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultados')
                
                st.download_button(
                    label="📥 Descargar Reporte Final en Excel (.xlsx)",
                    data=buffer.getvalue(),
                    file_name="reporte_auditoria_probidad.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.markdown("### Vista Previa de Resultados")
                # st.dataframe(df.style.applymap(lambda v: 'color: red; font-weight: bold;' if v == 'CON OBSERVACIÓN' else 'color: green;' if v == 'SIN HALLAZGOS' else '', subset=['Estado']))
                st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")