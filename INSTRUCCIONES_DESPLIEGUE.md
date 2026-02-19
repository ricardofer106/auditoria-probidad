# 🚀 Instrucciones de Despliegue en Streamlit Cloud

Como tu contraseña de Google Cloud no ha funcionado, la mejor opción (gratuita y rápida) es usar **Streamlit Cloud**.

## Pasos para subir tu App:

### 1. Crear Repositorio en GitHub
1.  Ve a [github.com/new](https://github.com/new).
2.  Crea un repositorio llamado `auditoria-probidad` (Público o Privado).
3.  **No añadas README ni .gitignore** (ya los tenemos).

### 2. Subir el Código (Desde tu terminal)
Copia y pega estos comandos en tu terminal de PowerShell (una línea a la vez):

```powershell
git remote add origin https://github.com/TU_USUARIO/auditoria-probidad.git
git push -u origin main
```
*(Reemplaza TU_USUARIO por tu nombre de usuario de GitHub)*.

### 3. Conectar con Streamlit Cloud
1.  Ve a [share.streamlit.io](https://share.streamlit.io/).
2.  Inicia sesión con tu cuenta de GitHub.
3.  Haz clic en **"New app"**.
4.  Selecciona tu repositorio (`auditoria-probidad`).
5.  En **"Main file path"**, escribe `app.py`.
6.  Haz clic en **"Deploy!"**.

¡Y listo! En unos 2-3 minutos tu aplicación estará en internet con un enlace seguro (`https://auditoria-probidad.streamlit.app`).

---
**Nota:** El archivo `requirements.txt` ya incluye todo lo necesario para que funcione en la nube.
