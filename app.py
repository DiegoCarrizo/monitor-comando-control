import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor C2 - ROD-71-01-II", layout="wide")

# Tablas Base (ROD-71-01-II Anexo 7)
VRC_PROPIOS = {"Ca I Mec (VCTP)": 1.0, "Esc Tan (TAM)": 2.0, "Esc Tan (TAM 2C)": 2.5, "Ba PP Cal 155": 1.0}
VRC_ENO = {"Ca I Mot": 0.40, "Esc Tan (Eno)": 1.5, "Ba Art": 0.8}
FACTORES_MORAL = {"Muy alta": 2.0, "Normal": 1.0, "Baja": 0.5}
FACTORES_TERRENO = {"Llanura": 1.0, "Monte": 0.5, "Urbano": 0.3}
PCR_REQUERIDO = {"Ataque Ruptura": 5.0, "Ataque Frontal": 3.0, "Defensa de Zona": 0.33}
DEGRADACION = {"Ataque Ruptura": 0.20, "Ataque Frontal": 0.15, "Defensa de Zona": 0.10}

if 'data' not in st.session_state:
    st.session_state.data = {
        'unidades_propias': [], 'unidades_eno': [],
        'moral': 1.0, 'terreno': 1.0, 'operacion': 'Ataque Frontal',
        'abastecimiento_clase_v': 100
    }

st.sidebar.title("Navegación Plana Mayor")
rol = st.sidebar.radio("Área:", ["G1 - Personal", "G2 - Inteligencia", "G3 - Operaciones", "G4 - Materiales", "Comandante"])

if rol == "G1 - Personal":
    st.header("G1: Estado de la Fuerza")
    moral_sel = st.selectbox("Nivel Moral", list(FACTORES_MORAL.keys()), index=1)
    st.session_state.data['moral'] = FACTORES_MORAL[moral_sel]
    st.info(f"Multiplicador de moral ajustado a {st.session_state.data['moral']}")

elif rol == "G2 - Inteligencia":
    st.header("G2: Ambiente y Enemigo")
    terr_sel = st.selectbox("Terreno Principal", list(FACTORES_TERRENO.keys()))
    st.session_state.data['terreno'] = FACTORES_TERRENO[terr_sel]
    
    st.subheader("Orden de Batalla Enemigo")
    unidad_eno = st.selectbox("Agregar Unidad Enemiga", list(VRC_ENO.keys()))
    if st.button("Sumar Fuerza Enemiga"):
        st.session_state.data['unidades_eno'].append({'Unidad': unidad_eno, 'VRC': VRC_ENO[unidad_eno]})
    if st.session_state.data['unidades_eno']:
        st.dataframe(pd.DataFrame(st.session_state.data['unidades_eno']))

elif rol == "G3 - Operaciones":
    st.header("G3: Maniobra y Poder de Combate")
    st.session_state.data['operacion'] = st.selectbox("Tipo de Operación Táctica", list(PCR_REQUERIDO.keys()))
    
    st.subheader("Organización para el Combate")
    unidad_propia = st.selectbox("Asignar Unidad Propia", list(VRC_PROPIOS.keys()))
    if st.button("Sumar a la Organización"):
        st.session_state.data['unidades_propias'].append({'Unidad': unidad_propia, 'VRC': VRC_PROPIOS[unidad_propia]})
    if st.session_state.data['unidades_propias']:
        st.dataframe(pd.DataFrame(st.session_state.data['unidades_propias']))

elif rol == "G4 - Materiales":
    st.header("G4: Sostenimiento Logístico")
    st.session_state.data['abastecimiento_clase_v'] = st.slider("Disponibilidad Munición (Clase V) %", 0, 100, 100)
    if st.session_state.data['abastecimiento_clase_v'] < 40:
        st.warning("Nivel crítico: Afecta la continuidad operacional.")

elif rol == "Comandante":
    st.header("Tablero de Comando y Control (C2)")
    
    vrc_bruto_propio = sum([u['VRC'] for u in st.session_state.data['unidades_propias']])
    vrc_bruto_eno = sum([u['VRC'] for u in st.session_state.data['unidades_eno']])
    
    poder_propio = vrc_bruto_propio * st.session_state.data['moral'] * st.session_state.data['terreno']
    poder_eno = vrc_bruto_eno * st.session_state.data['terreno']
    
    pcr_actual = poder_propio / poder_eno if poder_eno > 0 else 0
    pcr_exigido = PCR_REQUERIDO[st.session_state.data['operacion']]
    deg_estimada = DEGRADACION[st.session_state.data['operacion']] * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("PCR Actual", f"{pcr_actual:.2f}:1")
    col2.metric("PCR Doctrinario", f"{pcr_exigido}:1")
    col3.metric("Degradación Estimada", f"-{deg_estimada}%")
    
    if pcr_actual >= pcr_exigido and st.session_state.data['abastecimiento_clase_v'] >= 40:
        st.success("✅ OPERACIÓN FACTIBLE: El PCR supera el mínimo doctrinario.")
    else:
        st.error("⚠️ RIESGO TÁCTICO INACEPTABLE: No se alcanza el PCR o el sostenimiento es crítico.")
