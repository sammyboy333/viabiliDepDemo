import streamlit as st
import requests
import os
import time
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import streamlit.components.v1 as components
from datetime import datetime, timezone  # Import timezone for UTC-aware datetime
import warnings  # Import warnings module

GOOGLE_APPLICATION_CREDENTIALS = "templates/viabili-service-account.json"
CLOUD_RUN_URL = "https://viabili3-1041704460502.us-central1.run.app"

# Allow deprecation warnings
warnings.filterwarnings("default", category=DeprecationWarning)

# Configure Streamlit page
st.set_page_config(
    layout='wide', 
    initial_sidebar_state='expanded',
    page_title='Viabili - Análisis RFQ',
    page_icon="https://cdn.prod.website-files.com/640617b2f45b42597a76b590/6679b53c57f0356096fe4b48_logo-footer.svg"
)

# Apply basic styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Análisis RFQ")

# Option to toggle between ZIP upload and RFQ ID
upload_mode = st.sidebar.radio(
    "Selecciona el modo de carga:",
    options=["Subir ZIP ordenado", "RFQ ID (deshabilitado)"],
    index=0
)

if upload_mode == "Subir ZIP ordenado":
    # Display instructions for ZIP upload
    st.sidebar.markdown(
        """
        **Instrucciones:**
        1. Ordena tu carpeta en subcarpetas; una por cada Item (Ensamble o pieza).
        2. Comprime tu carpeta a un archivo ZIP.

        **Ejemplo de estructura:**
        ```
        📁 MiCarpeta  
        ├── 📁 Item1  
        │   ├── 📄 blueprint1.pdf  
        │   ├── 📄 blueprint2.png  
        ├── 📁 Item2  
        │   ├── 📄 blueprint3.jpg  
        │   ├── 📄 blueprint4.step  
        ```
        """
    )
    # ZIP upload option
    uploaded_zip = st.sidebar.file_uploader("Subir ZIP ordenado", type=["zip"])
    rfq_id = None  # Ensure RFQ ID is not set
else:
    # RFQ ID input (disabled)
    st.sidebar.warning("⚠️ Esta funcionalidad está temporalmente deshabilitada.")
    rfq_id = st.sidebar.text_input("ID de RFQ", value="", placeholder="Funcionalidad deshabilitada", disabled=True)
    uploaded_zip = None  # Ensure ZIP upload is not set

# Add link to Google Drive folder for previous reports
st.sidebar.markdown(
    """
    [¿Estás buscando un reporte que ya habías generado?](https://drive.google.com/drive/u/0/folders/0ACZWLfGMmMwLUk9PVA)
    """
)

# "Ejecutar" button
clicked = st.sidebar.button("Ejecutar")

# Initialize session state for persisting results
if "last_status" not in st.session_state:
    st.session_state.last_status = None
if "iframe_shown" not in st.session_state:
    st.session_state.iframe_shown = False
if "spreadsheet_url" not in st.session_state:
    st.session_state.spreadsheet_url = None

# Status box placeholder
status_box = st.empty()

# Display the last status if available
if st.session_state.last_status:
    last = st.session_state.last_status
    if "✅" in last or "completada exitosamente" in last.lower():
        status_box.success(last)
    elif "❌" in last or "error" in last.lower() or "fallida" in last.lower() or "no encontrado" in last.lower():
        status_box.error(last)
    else:
        status_box.info(last)

# Display the iframe if it was previously shown
if st.session_state.iframe_shown and st.session_state.spreadsheet_url and not clicked:
    components.html(
        f"""
        <iframe src="{st.session_state.spreadsheet_url}?widget=true&amp;headers=false"
                width="100%" height="600" style="border:none;"></iframe>
        """,
        height=600,
    )
    # Add a link to open the Google Sheet in a new tab
    st.markdown(
        f"[Ver más detalles en Sheets]({st.session_state.spreadsheet_url})",
        unsafe_allow_html=True
    )

if clicked:
    st.session_state.iframe_shown = False
    st.session_state.last_status = None
    st.session_state.spreadsheet_url = None
    status_box.empty()
    components.html("", height=0)

    creds = service_account.IDTokenCredentials.from_service_account_file(
        GOOGLE_APPLICATION_CREDENTIALS,
        target_audience=CLOUD_RUN_URL
    )
    # Refresh credentials to populate expiry
    creds.refresh(Request())
    # Ensure timezone-aware datetime is used
    if creds.expiry:
        creds.expiry = datetime.fromtimestamp(creds.expiry.timestamp(), tz=timezone.utc)
    headers = {"Authorization": f"Bearer {creds.token}"}

    # **INPUT VALIDATION:**
    if uploaded_zip is None and not (rfq_id and rfq_id.isdigit()):
        st.sidebar.error("Por favor, selecciona un ZIP válido o ingresa un ID de RFQ válido.")
        st.stop()

    if uploaded_zip is not None:
        # Manual ZIP upload - preserve original filename
        original_filename = uploaded_zip.name
        zip_path = original_filename
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())
        status_box.info("📤 Subiendo ZIP manual al API de Cloud Run...")
        with open(zip_path, "rb") as f:
            files = {"file": (original_filename, f, "application/zip")}
            response = requests.post(
                f"{CLOUD_RUN_URL}/upload-zip/",
                files=files,
                headers=headers,
                params={"skip_sort": "true"}
            )
        os.remove(zip_path)
    elif rfq_id and rfq_id.isdigit():
        # RFQ-based processing (experimental - currently disabled)
        status_box.error("❌ La funcionalidad de RFQ ID está temporalmente deshabilitada. Por favor, usa la opción de subir ZIP.")
        st.session_state.last_status = "❌ La funcionalidad de RFQ ID está temporalmente deshabilitada."
        st.stop()

    if response.status_code == 200:
        task_id = response.json().get("task_id")
        status_box.info("📊 Procesando tarea...")
        with st.spinner("⏳ Procesando, por favor espera..."):
            retry_attempts = 5  # Number of retries for task status
            while True:
                try:
                    task_status_response = requests.get(f"{CLOUD_RUN_URL}/task-status/{task_id}", headers=headers)
                    task_status = task_status_response.json()
                    current_status = task_status.get("status")
                    if current_status.lower() == "completado":
                        status_box.success("Tarea completada exitosamente.")
                        st.session_state.last_status = "Tarea completada exitosamente."
                        st.session_state.iframe_shown = True
                        st.session_state.spreadsheet_url = task_status.get("spreadsheet_url")
                        components.html(
                            f"""
                            <iframe src="{st.session_state.spreadsheet_url}?widget=true&amp;headers=false"
                                    width="100%" height="600" style="border:none;"></iframe>
                            """,
                            height=600,
                        )
                        # Add a link to open the Google Sheet in a new tab
                        st.markdown(
                            f"[Ver más detalles en Sheets]({st.session_state.spreadsheet_url})",
                            unsafe_allow_html=True
                        )
                        break
                    elif current_status.startswith("error"):
                        status_box.error(f"Tarea fallida: {current_status}")
                        st.session_state.last_status = f"Tarea fallida: {current_status}"
                        break
                    else:
                        status_box.info(current_status.capitalize())
                        st.session_state.last_status = current_status.capitalize()
                except requests.JSONDecodeError:
                    if retry_attempts > 0:
                        retry_attempts -= 1
                        time.sleep(3)  # Wait before retrying
                        continue
                    else:
                        status_box.error("❌ Error al decodificar la respuesta JSON después de varios intentos.")
                        st.session_state.last_status = "❌ Error al decodificar la respuesta JSON después de varios intentos."
                        break
                except requests.exceptions.RequestException as e:
                    status_box.error(f"Error de red: {e}")
                    st.session_state.last_status = f"Error de red: {e}"
                    break
                time.sleep(3)
    else:
        status_box.error(f"❌ Error al iniciar la tarea. Código HTTP: {response.status_code}")
        st.session_state.last_status = f"❌ Error al iniciar la tarea. Código HTTP: {response.status_code}"
        st.session_state.last_status = f"❌ Error al iniciar la tarea. Código HTTP: {response.status_code}"
