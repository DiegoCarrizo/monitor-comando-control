import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor C2 - Plana Mayor", layout="wide")

# Inicialización de variables de estado
if 'datos' not in st.session_state:
    st.session_state.datos = {
        'moral': 1.0, 'terreno': 1.0, 
        'vrc_propio': 10.0, 'vrc_eno': 5.0,
        'operacion': 'Ataque Frontal', 'pcr_req': 3.0
    }

# Navegación
rol = st.sidebar.radio("Área de Conducción", 
    ["Personal", "Inteligencia", "Operaciones", "Materiales", "Jefe Plana Mayor", "Jefe de Elemento"])

# --- PANELES DE LA PLANA MAYOR ---
if rol == "Personal":
    st.title("Panel de Personal")
    moral_input = st.selectbox("Estado Moral de la Tropa", ["Muy alta (2.0)", "Normal (1.0)", "Baja (0.5)"])
    st.session_state.datos['moral'] = float(moral_input.split("(")[1].replace(")",""))
    st.success("Variables de personal actualizadas.")

elif rol == "Inteligencia":
    st.title("Panel de Inteligencia")
    st.session_state.datos['vrc_eno'] = st.number_input("Valor Relativo de Combate (VRC) Enemigo", value=st.session_state.datos['vrc_eno'])
    terreno_input = st.selectbox("Factor de Terreno (Aptitud)", ["Llanura (1.0)", "Monte (0.5)", "Urbano (0.3)"])
    st.session_state.datos['terreno'] = float(terreno_input.split("(")[1].replace(")",""))

elif rol == "Operaciones":
    st.title("Panel de Operaciones")
    st.session_state.datos['vrc_propio'] = st.number_input("VRC Propio (Base)", value=st.session_state.datos['vrc_propio'])
    op = st.selectbox("Tipo de Operación", ["Ataque Frontal", "Ataque Ruptura", "Defensa de Zona"])
    pcr_dict = {"Ataque Frontal": 3.0, "Ataque Ruptura": 5.0, "Defensa de Zona": 0.33}
    st.session_state.datos['operacion'] = op
    st.session_state.datos['pcr_req'] = pcr_dict[op]

elif rol == "Jefe Plana Mayor":
    st.title("Síntesis del Estado Mayor")
    st.write(pd.DataFrame([st.session_state.datos]))
    st.info("Verificando factibilidad y aceptabilidad de los Modos de Acción...")

# --- PANEL DEL COMANDANTE ---
elif rol == "Jefe de Elemento":
    st.title("Tablero de Resolución y Alertas")
    
    d = st.session_state.datos
    poder_propio_ajustado = d['vrc_propio'] * d['moral'] * d['terreno']
    poder_eno_ajustado = d['vrc_eno'] * d['terreno']
    
    pcr_real = poder_propio_ajustado / poder_eno_ajustado if poder_eno_ajustado > 0 else 0
    
    st.metric("PCR Calculado", f"{pcr_real:.2f} : 1")
    st.metric("PCR Doctrinario Requerido", f"{d['pcr_req']} : 1")
    
    if pcr_real >= d['pcr_req']:
        st.success("✅ MODO DE ACCIÓN ACEPTABLE: El Poder de Combate Relativo supera las exigencias de la operación.")
    else:
        st.error("⚠️ ALERTA DE RIESGO TÁCTICO: El modo de acción elegido tiene alta probabilidad de fracaso. El PCR actual no alcanza el umbral mínimo.")