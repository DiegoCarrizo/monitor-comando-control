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
# ----------------- PANEL G1 -----------------
if rol == "G1 - Personal":
    st.header("G1: Carga Manual y Cálculo Analítico de Personal")
    st.markdown("Evaluación matemática según parámetros de experiencia y bajas (Ref. ROD-71-01-II, Anexo 7)[cite: 1]")
    
    # 1. Efectivos y Experiencia
    st.subheader("1. Efectivos y Experiencia de Combate")
    col1, col2 = st.columns(2)
    with col1:
        total_efectivos = st.number_input("Total de Efectivos", min_value=1, value=100)
    with col2:
        exp_combate = st.number_input("Personal con Experiencia en Combate", min_value=0, max_value=total_efectivos, value=0)
    
    # 2. Instrucción
    st.subheader("2. Nivel de Instrucción")
    niveles = {"Alta instrucción": 1.0, "Mediana instrucción": 0.75, "Baja instrucción": 0.5}
    col_of, col_subof, col_sold = st.columns(3)
    with col_of:
        inst_of = st.selectbox("Oficiales", list(niveles.keys()), index=0)
    with col_subof:
        inst_subof = st.selectbox("Suboficiales", list(niveles.keys()), index=0)
    with col_sold:
        inst_sold = st.selectbox("Soldados", list(niveles.keys()), index=1)
        
    # 3. Bajas (Estado de Fuerzas)
    st.subheader("3. Bajas y Fricción (Desgaste)")
    cb1, cb2, cb3, cb4 = st.columns(4)
    with cb1:
        muertos = st.number_input("Muertos (KIA)", min_value=0, value=0)
    with cb2:
        heridos = st.number_input("Heridos (WIA)", min_value=0, value=0)
    with cb3:
        desaparecidos = st.number_input("Desaparecidos (MIA)", min_value=0, value=0)
    with cb4:
        desertores = st.number_input("Desertores", min_value=0, value=0)
        
    # --- CÁLCULO MATEMÁTICO ---
    
    # A. Experiencia (Fórmula ROD-71-01-II)[cite: 1]
    sin_exp = total_efectivos - exp_combate
    factor_exp = ((sin_exp * 0.1) + (exp_combate * 1.0)) / total_efectivos
    st.session_state.g1['experiencia'] = factor_exp
    
    # B. Instrucción (Promedio ponderado del cuadro)
    factor_instruccion = (niveles[inst_of] + niveles[inst_subof] + niveles[inst_sold]) / 3
    st.session_state.g1['personal_permanente'] = factor_instruccion
    
    # C. Moral (Modelo matemático por impacto de bajas)
    bajas_totales = muertos + heridos + desaparecidos + desertores
    efectivos_reales = total_efectivos - bajas_totales
    
    impacto_moral = 0
    if total_efectivos > 0:
        # Los heridos y desaparecidos tienen impacto lineal. Los muertos y desertores castigan el doble la moral.
        impacto_bajas = (heridos + desaparecidos) / total_efectivos
        impacto_critico = (muertos + (desertores * 2)) / total_efectivos 
        impacto_moral = impacto_bajas + impacto_critico
        
    # Asignación de escala doctrinaria (ROD-71-01-II)[cite: 1]
    if impacto_moral == 0 and factor_instruccion > 0.8:
        moral_calc = 2.0
        moral_text = "Muy Alta"
    elif impacto_moral < 0.05:
        moral_calc = 1.5
        moral_text = "Alta"
    elif impacto_moral < 0.15:
        moral_calc = 1.0
        moral_text = "Normal"
    elif impacto_moral < 0.30:
        moral_calc = 0.5
        moral_text = "Baja"
    else:
        moral_calc = 0.2
        moral_text = "Muy Baja"
        
    st.session_state.g1['moral'] = moral_calc
    
    # --- RESULTADOS ---
    st.divider()
    st.subheader("Síntesis del Panel G1")
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Efectivos en Condiciones", f"{efectivos_reales}", f"-{bajas_totales} bajas totales", delta_color="inverse")
    rc2.metric("Estado Moral Calculado", moral_text, f"Multiplicador: {moral_calc}")
    
    # Capacidad de Combate según Personal (Multiplicador Compuesto)
    capacidad_personal = factor_exp * factor_instruccion * moral_calc
    rc3.metric("Capacidad de Combate (Personal)", f"{capacidad_personal:.2f}", "Fuerza Humana Ponderada")
    
    st.info("Los coeficientes matemáticos de moral, instrucción y experiencia han sido enviados al Tablero del Comandante para ajustar el PCR general.")
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
