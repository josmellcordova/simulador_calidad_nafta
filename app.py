import streamlit as st
import pandas as pd
import joblib

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Predictor T90 Nafta - Flexicoking", page_icon="🛢️", layout="centered")
st.title("🛢️ Simulador de Calidad de Nafta (T90)")
st.markdown("Mueva los controles para simular la dinámica de la columna.")

# ==========================================
# 2. CARGA DEL MODELO ENTRENADO
# ==========================================
@st.cache_resource
def cargar_modelo():
    return joblib.load('modelo_flexicoking_nafta_v1.pkl')

try:
    modelo_produccion = cargar_modelo()
    variables_requeridas = modelo_produccion.feature_names_in_
except Exception as e:
    st.error("⚠️ Error Crítico: No se encontró el archivo 'modelo_flexicoking_nafta_v1.pkl'.")
    st.stop()

# ==========================================
# 3. CONFIGURACIÓN DEL DICCIONARIO (LÍMITES Y DESCRIPCIONES)
# ==========================================
# Agregamos la clave "desc" a cada variable
CONFIGURACION_VARIABLES = {
    "DT3": {
        "min": 20.0, "max": 100.0, "default": 70.0,
        "desc": "Diferencia de temperatura entre TI20308 y TI20305."
    },
    "FC20101": {
        "min": 50.0, "max": 200.0, "default": 100.0,
        "desc": "Flujo MPA lavado."
    },
    "TC20301": {
        "min": 80.0, "max": 130.0, "default": 108.0,
        "desc": "Temperatura de tope del fraccionador."

    },
    "BPA_duty": {
        "min": 0.0, "max": 5.0, "default": 3.0,
        "desc": "Duty BPA."

    },
    "TI20305": {
        "min": 140.0, "max": 200.0, "default": 165.0,
        "desc": "Temperatura Downcomer Plato 5."

    },
    "MPA_duty": {
        "min": 0.0, "max": 10.0, "default": 7.0,
        "desc": "Duty MPA."

    },
    "TC10501": {
        "min": 370.0, "max": 420.0, "default": 390.0,
        "desc": "Temperatura de tope del scrubber."

    }
    # Agrega tus demás variables aquí siguiendo exactamente este mismo formato...
}

# ==========================================
# 4. INTERFAZ LATERAL: CONTROLES Y DESCRIPCIONES
# ==========================================
st.sidebar.header("⚙️ Panel de Operación")
valores_ingresados = {}

for variable in variables_requeridas:
    # Buscamos la configuración; si no la has definido, usa valores por defecto
    config = CONFIGURACION_VARIABLES.get(variable, {
        "min": 0.0, "max": 300.0, "default": 150.0,
        "desc": "Variable operativa del proceso."
    })

    # OPCIÓN 1: Texto visible directamente debajo de la variable
    st.sidebar.caption(f"ℹ️ {config['desc']}")

    # Creamos el control deslizante
    valores_ingresados[variable] = st.sidebar.slider(
        label=f"{variable}",
        min_value=float(config["min"]),
        max_value=float(config["max"]),
        value=float(config["default"]),
        step=0.1,
        #help=config["desc"]  # OPCIÓN 2: Icono de ayuda (?) al lado del nombre
    )

    # Línea divisoria suave para separar cada variable y que no se vea amontonado
    st.sidebar.divider()

# ==========================================
# 5. MOTOR DE PREDICCIÓN Y RESULTADOS
# ==========================================
datos_simulacion = pd.DataFrame([valores_ingresados])
st.subheader("📊 Resultado de la Simulación")

if st.button("Calcular T90 Proyectado", type="primary"):
    prediccion = modelo_produccion.predict(datos_simulacion)[0]
    LIMITE_FBP = 173.0

    if prediccion <= LIMITE_FBP:
        st.success("✅ Nafta dentro de especificación comercial.")
        st.metric(label="T90 Estimado", value=f"{prediccion:.1f} °C", delta="Operación Segura")
    else:
        st.error(f"⚠️ ALARMA TÉRMICA: Nafta fuera de especificación (> {LIMITE_FBP} °C).")
        st.metric(label="T90 Estimado", value=f"{prediccion:.1f} °C", delta="¡Modificar Parámetros!", delta_color="inverse")

# Pie de página operativo
st.markdown("---")
st.caption("Modelo: Linear Regression + RFECV | Realizado por Josmell Córdova Claros")
