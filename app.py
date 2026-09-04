import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor C2 - Estado Mayor", layout="wide")

# Inicialización de la base de datos temporal en memoria
if 'g1' not in st.session_state:
    st.session_state.g1 = {'experiencia': 1.0, 'personal_permanente': 1.0, 'moral': 1.0}
if 'g2' not in st.session_state:
    st.session_state.g2 = {'terreno': 1.0, 'clima': 1.0, 'fuerzas_eno': []}
if 'g3' not in st.session_state:
    st.session_state.g3 = {'fuerzas_propias': [], 'tipo_operacion': 'Ataque Frontal', 'pcr_requerido': 3.0}
if 'g4' not in st.session_state:
    st.session_state.g4 = {'clase_i': 100, 'clase_iii': 100, 'clase_v': 100, 'vehiculos_servicio': 100}

# Menú lateral
st.sidebar.title("Áreas de Conducción")
rol = st.sidebar.radio("Seleccione Panel:", ["G1 - Personal", "G2 - Inteligencia", "G3 - Operaciones", "G4 - Materiales", "Comandante"])

# ----------------- PANEL G1 -----------------
if rol == "G1 - Personal":
    st.header("G1: Carga Manual de Factores Multiplicadores de Personal")
    st.markdown("Según Anexo 7 - Tabla II[cite: 1]")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.g1['moral'] = st.number_input("Multiplicador de Moral (Ej: Muy alta=2.0, Normal=1.0, Baja=0.5)", value=st.session_state.g1['moral'], step=0.1)
        st.session_state.g1['experiencia'] = st.number_input("Experiencia de Combate (Móvil=1.0, Defensivo=0.5, Sin exp=0.1)", value=st.session_state.g1['experiencia'], step=0.1)
    with col2:
        st.session_state.g1['personal_permanente'] = st.number_input("Composición (% Permanente: 100%=1.0, 75%=0.75)", value=st.session_state.g1['personal_permanente'], step=0.05)
    
    st.success("Parámetros de fuerza humana actualizados en el modelo.")

# ----------------- PANEL G2 -----------------
elif rol == "G2 - Inteligencia":
    st.header("G2: Carga Manual de Enemigo y Ambiente Operacional")
    st.markdown("Cálculos de fricción geográfica (Anexo 7 - Tabla I)[cite: 1]")
    
    col_t, col_c = st.columns(2)
    with col_t:
        st.session_state.g2['terreno'] = st.number_input("Multiplicador de Terreno (Llanura=1.0, Monte=0.5, Montaña=0.1)", value=st.session_state.g2['terreno'], step=0.1)
    with col_c:
        st.session_state.g2['clima'] = st.number_input("Multiplicador de Clima/Aclimatación (0.1 a 1.0)", value=st.session_state.g2['clima'], step=0.1)
    
    st.divider()
    st.subheader("Orden de Batalla Enemigo (Manual)")
    with st.form("form_eno"):
        tipo_eno = st.text_input("Elemento Enemigo Detectado (Ej: Ca I Mec Eno)")
        vrc_eno = st.number_input("Valor Relativo de Combate (VRC)", min_value=0.0, step=0.1)
        submit_eno = st.form_submit_button("Cargar Fuerza Enemiga")
        if submit_eno and tipo_eno:
            st.session_state.g2['fuerzas_eno'].append({'Elemento': tipo_eno, 'VRC': vrc_eno})
            
    if st.session_state.g2['fuerzas_eno']:
        st.dataframe(pd.DataFrame(st.session_state.g2['fuerzas_eno']), use_container_width=True)

# ----------------- PANEL G3 -----------------
elif rol == "G3 - Operaciones":
    st.header("G3: Maniobra, Exploración y Poder de Combate Propio")
    
    op = st.selectbox("Operación Táctica (Fija el PCR Requerido)", ["Ataque Ruptura (5:1)", "Ataque Frontal (3:1)", "Defensa de Zona (0.33:1)", "Retardo (0.33:1)"])
    st.session_state.g3['tipo_operacion'] = op.split(" ")[0]
    st.session_state.g3['pcr_requerido'] = float(op.split("(")[1].split(":")[0])
    
    st.divider()
    st.subheader("Carga Manual de Organización para el Combate")
    st.markdown("Incluya explícitamente elementos maniobra y **elementos de exploración** (Ej: Esc Expl Guaraní VRC 0.90, Sec Expl Moto TT VRC 0.10)[cite: 1]")
    
    with st.form("form_propio"):
        cat_propia = st.selectbox("Categoría", ["Combate Directo (Blindado/Mec)", "Exploración y Seguridad", "Apoyo de Fuego", "Ingenieros"])
        tipo_propio = st.text_input("Denominación del Elemento (Ej: Esc Expl Cab Bl 11)")
        vrc_propio = st.number_input("Valor Relativo de Combate (VRC)", min_value=0.0, step=0.1)
        submit_propio = st.form_submit_button("Cargar Fuerza Propia")
        if submit_propio and tipo_propio:
            st.session_state.g3['fuerzas_propias'].append({'Categoría': cat_propia, 'Elemento': tipo_propio, 'VRC': vrc_propio})
            
    if st.session_state.g3['fuerzas_propias']:
        st.dataframe(pd.DataFrame(st.session_state.g3['fuerzas_propias']), use_container_width=True)

# ----------------- PANEL G4 -----------------
elif rol == "G4 - Materiales":
    st.header("G4: Sostenimiento y Restricciones Logísticas")
    st.markdown("Defina los porcentajes actuales de abastecimiento operativo.")
    
    st.session_state.g4['clase_i'] = st.slider("Clase I (Racionamiento) %", 0, 100, st.session_state.g4['clase_i'])
    st.session_state.g4['clase_iii'] = st.slider("Clase III (Combustibles y Lubricantes) %", 0, 100, st.session_state.g4['clase_iii'])
    st.session_state.g4['clase_v'] = st.slider("Clase V (Munición) %", 0, 100, st.session_state.g4['clase_v'])
    st.session_state.g4['vehiculos_servicio'] = st.slider("Tasa de Vehículos en Servicio (Mantenimiento) %", 0, 100, st.session_state.g4['vehiculos_servicio'])

# ----------------- PANEL COMANDANTE -----------------
elif rol == "Comandante":
    st.header("Tablero de Comando y Resolución (Modelo Matemático)")
    
    # Cálculos dinámicos
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.g3['fuerzas_propias'])
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.g2['fuerzas_eno'])
    
    # Factor multiplicador G1 (Promedio de variables según Tabla II)[cite: 1]
    multiplicador_g1 = (st.session_state.g1['moral'] * st.session_state.g1['personal_permanente'] * st.session_state.g1['experiencia'])
    
    # Poder ajustado
    poder_propio = vrc_base_propio * multiplicador_g1 * st.session_state.g2['terreno'] * st.session_state.g2['clima']
    poder_eno = vrc_base_eno * st.session_state.g2['terreno']
    
    pcr_real = poder_propio / poder_eno if poder_eno > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Poder de Combate Propio (Ajustado)", f"{poder_propio:.2f}")
    col2.metric("Poder de Combate Eno (Ajustado)", f"{poder_eno:.2f}")
    col3.metric("PCR RESULTANTE", f"{pcr_real:.2f} : 1")
    
    st.divider()
    st.subheader("Análisis de Factibilidad y Aceptabilidad")
    
    exigencia_pcr = st.session_state.g3['pcr_requerido']
    alerta_logistica = any(val < 50 for val in st.session_state.g4.values())
    
    if pcr_real >= exigencia_pcr and not alerta_logistica:
        st.success(f"✅ FACTIBLE: El PCR actual ({pcr_real:.2f}) es suficiente para la operación de {st.session_state.g3['tipo_operacion']} (Requiere {exigencia_pcr}). Logística en parámetros aceptables.")
    elif pcr_real < exigencia_pcr:
        st.error(f"⚠️ RIESGO MATEMÁTICO: El PCR de {pcr_real:.2f} es inferior al umbral doctrinario de {exigencia_pcr} para esta operación.")
    
    if alerta_logistica:
        st.warning("⚠️ ALERTA LOGÍSTICA (G4): Al menos una clase de abastecimiento o la tasa de mantenimiento se encuentra por debajo del 50%, amenazando la continuidad operacional.")
