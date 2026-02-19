# 🛡️ Portal de Auditoría de Probidad - Documentación Técnica

## 📌 ¿Qué hace esta aplicación?
Esta es una herramienta automatizada de auditoría diseñada para detectar conflictos de interés en funcionarios públicos. Su objetivo principal es **cruzar masivamente** las declaraciones de intereses y patrimonio con la base de datos de proveedores del Estado.

## ⚙️ ¿Cómo lo hace?

### 1. Lectura Inteligente de Datos
- **Carga de Archivos**: Permite subir un archivo Excel/CSV con las declaraciones.
- **Detección Automática**:
  - Identifica el formato del archivo (UTF-8 o Latin-1).
  - Busca columnas clave ("RUT Declarante", "Cónyuge", "Sociedades") incluso si los nombres varían ligeramente.

### 2. Extracción Exhaustiva de Información (Regex)
La aplicación no se limita a las columnas principales. Utiliza **Expresiones Regulares (Regex)** para escanear **toda la fila** de cada funcionario.
- **Busca patrones de RUT**: `\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b`
- Esto significa que si en la columna "Observaciones" o "Hijos" aparece un texto como *"Socio Juan Perez 12.345.678-9"*, el sistema **capturará ese RUT automáticamente** para auditarlo.

### 3. Cruce de Información (Con Mercado Público)
Cada RUT encontrado (ya sea del funcionario, cónyuge o extraído del texto) se somete a un proceso de verificación:
1.  **Normalización**: Se limpia el RUT (quita puntos, guiones, espacios) y se vuelve a formatear al estándar oficial (con puntos y guión).
2.  **Consulta Externa**: Se conecta en tiempo real al portal de **Mercado Público** (`https://www.mercadopublico.cl/Portal/V2/BusquedaProveedores?rut=...`).
3.  **Análisis de Respuesta**: Lee el HTML de la página de resultados para determinar si la persona/empresa figura como "Proveedor Vigente".

### 4. Detección de Sociedades
Paralelamente, revisa la columna de declaración de sociedades.
- Si el texto indica participación (cualquier cosa distinta a "No posee", "Sin información", etc.), se levanta una alerta preventiva.

## 🛠️ Tecnologías Utilizadas

- **Python 3**: Lenguaje principal de programación.
- **Streamlit**: Framework para crear la interfaz web interactiva.
- **Pandas**: Librería potente para la manipulación y análisis de datos (tablas CSV/Excel).
- **Requests**: Para realizar las peticiones HTTP a Mercado Público.
- **Re (Regular Expressions)**: Para la búsqueda avanzada de patrones de RUT en textos.
- **OpenPyXL**: Para la generación de reportes en formato Excel moderno (.xlsx).

## 🚀 Flujo de Uso
1.  Usuario sube CSV.
2.  Sistema procesa fila a fila, mostrando una barra de progreso.
3.  **Alertas en Tiempo Real**: Si detecta un hallazgo, muestra una alerta amarilla en pantalla con el detalle específico (ej: *"CÓNYUGE es proveedor"*).
4.  **Descarga Segura**: Genera un archivo Excel "limpio" (idéntico al original) para mantener la integridad de los datos base, dejando los hallazgos visibles solo en la auditoría en vivo.
