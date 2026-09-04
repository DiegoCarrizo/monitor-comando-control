import streamlit as st
import pandas as pd

st.set_page_config(page_title="Monitor C2 - Estado Mayor", layout="wide")

# Inicialización de la base de datos temporal en memoria
if 'g1' not in st.session_state:
    st.session_state.g1 = {'experiencia': 1.0, 'personal_permanente': 1.0, 'moral': 1.0}
if 'g2' not in st.session_state:
    st.session_state.g2 = {'terreno': 1.0, 'clima': 1.0, 'fuerzas_eno': [], 'ambiente': 'Llanura'}
if 'g3' not in st.session_state:
    st.session_state.g3 = {'fuerzas_propias': [], 'tipo_operacion': 'Ataque Frontal', 'pcr_requerido': 3.0}
if 'g4' not in st.session_state:
    st.session_state.g4 = {'clase_i': 100, 'clase_iii': 100, 'clase_v': 100, 'vehiculos_servicio': 100}

# Menú lateral
st.sidebar.title("Áreas de Conducción")
rol = st.sidebar.radio("Seleccione Panel:", ["G1 - Personal", "G2 - Inteligencia", "G3 - Operaciones", "G4 - Materiales", "Jefe de la Plana Mayor", "Comandante", "Gestión de Datos"])

# ----------------- PANEL G1 -----------------
if rol == "G1 - Personal":
    st.header("G1: Carga Manual y Cálculo Analítico de Personal")
    
    st.subheader("1. Efectivos y Experiencia de Combate")
    col1, col2 = st.columns(2)
    with col1:
        total_efectivos = st.number_input("Total de Efectivos", min_value=1, value=100)
    with col2:
        exp_combate = st.number_input("Personal con Experiencia en Combate", min_value=0, max_value=total_efectivos, value=0)
    
    st.subheader("2. Nivel de Instrucción")
    niveles = {"Alta instrucción": 1.0, "Mediana instrucción": 0.75, "Baja instrucción": 0.5}
    col_of, col_subof, col_sold = st.columns(3)
    with col_of:
        inst_of = st.selectbox("Oficiales", list(niveles.keys()), index=0)
    with col_subof:
        inst_subof = st.selectbox("Suboficiales", list(niveles.keys()), index=0)
    with col_sold:
        inst_sold = st.selectbox("Soldados", list(niveles.keys()), index=1)
        
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
        
    sin_exp = total_efectivos - exp_combate
    factor_exp = ((sin_exp * 0.1) + (exp_combate * 1.0)) / total_efectivos
    st.session_state.g1['experiencia'] = factor_exp
    
    factor_instruccion = (niveles[inst_of] + niveles[inst_subof] + niveles[inst_sold]) / 3
    st.session_state.g1['personal_permanente'] = factor_instruccion
    
    bajas_totales = muertos + heridos + desaparecidos + desertores
    efectivos_reales = total_efectivos - bajas_totales
    
    impacto_moral = 0
    if total_efectivos > 0:
        impacto_bajas = (heridos + desaparecidos) / total_efectivos
        impacto_critico = (muertos + (desertores * 2)) / total_efectivos 
        impacto_moral = impacto_bajas + impacto_critico
        
    if impacto_moral == 0 and factor_instruccion > 0.8:
        moral_calc = 2.0; moral_text = "Muy Alta"
    elif impacto_moral < 0.05:
        moral_calc = 1.5; moral_text = "Alta"
    elif impacto_moral < 0.15:
        moral_calc = 1.0; moral_text = "Normal"
    elif impacto_moral < 0.30:
        moral_calc = 0.5; moral_text = "Baja"
    else:
        moral_calc = 0.2; moral_text = "Muy Baja"
        
    st.session_state.g1['moral'] = moral_calc
    
    st.divider()
    st.subheader("Síntesis del Panel G1")
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Efectivos en Condiciones", f"{efectivos_reales}", f"-{bajas_totales} bajas")
    rc2.metric("Estado Moral Calculado", moral_text, f"Multiplicador: {moral_calc}")
    capacidad_personal = factor_exp * factor_instruccion * moral_calc
    rc3.metric("Capacidad de Combate", f"{capacidad_personal:.2f}")

# ----------------- PANEL G2 -----------------
elif rol == "G2 - Inteligencia":
    st.header("G2: Ambiente Geográfico y Orden de Batalla Enemigo")
    
    st.subheader("1. Entorno y Terreno a Operar")
    ambientes = ["Insular", "Desértico", "Desértico Patagónico", "Montaña", "Monte", "Llanura", "Urbano"]
    st.session_state.g2['ambiente'] = st.selectbox("Ambiente Geográfico", ambientes)
    
    terreno_eno = st.selectbox("Aptitud del Terreno para el Enemigo", ["Favorable", "Limitado", "Desfavorable"])
    mod_terreno = {"Favorable": 1.2, "Limitado": 0.8, "Desfavorable": 0.5}
    st.session_state.g2['terreno'] = mod_terreno[terreno_eno]
    
    st.divider()
    st.subheader("2. Ponderación Analítica de Elementos Enemigos")
    
    with st.form("form_eno_avanzado"):
        tipo_eno = st.text_input("Denominación del Elemento (Ej: Batallón de Infantería Enemigo)")
        col_fza, col_alc = st.columns(2)
        with col_fza:
            efectivos_pie = st.number_input("Número Relativo de Fuerzas a Pie", min_value=0, value=100)
            autonomia = st.number_input("Autonomía Operativa (Km)", min_value=0.0, value=50.0, step=10.0)
        with col_alc:
            alcance_armas = st.number_input("Alcance Promedio Armas (Km)", min_value=0.0, value=2.0, step=0.1)
            
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            has_drones = st.checkbox("Sistemas Drones / UAS")
        with col_t2:
            has_nocturna = st.checkbox("Capacidad Nocturna Estándar")
        with col_t3:
            has_termografica = st.checkbox("Visión Termográfica Avanzada")
            
        submit_eno = st.form_submit_button("Calcular VRC y Cargar al Tablero")
        
        if submit_eno and tipo_eno:
            vrc_base = (efectivos_pie * 0.01) + (alcance_armas * 0.15) + (autonomia * 0.005)
            mod_drones = 1.25 if has_drones else 1.0
            mod_optica = 1.35 if has_termografica else (1.15 if has_nocturna else 1.0)
            vrc_calculado = vrc_base * mod_drones * mod_optica
            
            st.session_state.g2['fuerzas_eno'].append({
                'Elemento': tipo_eno, 'VRC': round(vrc_calculado, 2),
                'Base': round(vrc_base, 2), 'Armas(Km)': alcance_armas, 'Fza Pie': efectivos_pie
            })
            
    if st.session_state.g2['fuerzas_eno']:
        st.dataframe(pd.DataFrame(st.session_state.g2['fuerzas_eno']), use_container_width=True)

# ----------------- PANEL G3 -----------------
elif rol == "G3 - Operaciones":
    st.header("G3: Maniobra, Exploración y Poder de Combate Propio")
    
    tipo_op_principal = st.selectbox("Clasificación de la Operación", ["Ofensiva", "Defensiva", "Complementaria"])
    
    if tipo_op_principal == "Ofensiva":
        op_detallada = st.selectbox("Tipo", ["Ataque Ruptura (5:1)", "Ataque Frontal (3:1)", "Ataque Envolvente", "Explotación"])
    elif tipo_op_principal == "Defensiva":
        op_detallada = st.selectbox("Tipo", ["Defensa de Zona (0.33:1)", "Defensa Móvil", "Acción Retardante"])
    else:
        op_detallada = st.selectbox("Tipo", ["Exploración", "Seguridad", "Marcha de Aproximación", "Infiltración"])
        
    st.session_state.g3['tipo_operacion'] = op_detallada.split(" ")[0]
    
    if "(" in op_detallada:
        st.session_state.g3['pcr_requerido'] = float(op_detallada.split("(")[1].split(":")[0])
    else:
        st.session_state.g3['pcr_requerido'] = 1.0
        
    st.divider()
    
    with st.form("form_op_propia"):
        elemento_nombre = st.text_input("Unidad / Fracción a emplear")
        col_amb, col_luz = st.columns(2)
        with col_amb:
            ambiente = st.selectbox("Ambiente Geográfico", ["Insular", "Desértico", "Desértico Patagónico", "Montaña", "Monte", "Llanura", "Urbano"], index=5)
        with col_luz:
            condicion_luz = st.selectbox("Condición de Iluminación", ["Diurna", "Nocturna"])
            
        col_p, col_a, col_v = st.columns(3)
        with col_p:
            efectivos = st.number_input("Cantidad de Personal Empleado", min_value=1, value=50)
        with col_a:
            alcance = st.number_input("Alcance Promedio Armamento (Km)", min_value=0.0, value=2.5, step=0.1)
        with col_v:
            autonomia = st.number_input("Autonomía de Vehículos (Km)", min_value=0.0, value=300.0, step=10.0)
            
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            vn_estandar = st.checkbox("Visión Nocturna Estándar")
        with col_v2:
            vn_termo = st.checkbox("Visión Termográfica")
            
        tiempo_est = st.number_input("Tiempo Estimado de Ejecución (Horas)", min_value=1, value=12)
        fases_op = st.text_area("Fases de la Operación")
        
        submit_g3 = st.form_submit_button("Calcular PCR y Asignar")
        
        if submit_g3 and elemento_nombre:
            vrc_base = (efectivos * 0.01) + (alcance * 0.15) + (autonomia * 0.005)
            mod_optica = 1.0
            if condicion_luz == "Nocturna":
                if vn_termo:
                    mod_optica = 1.5
                elif vn_estandar:
                    mod_optica = 1.0
                else:
                    mod_optica = 0.5
            
            moral_actual = st.session_state.g1.get('moral', 1.0)
            vrc_final = vrc_base * mod_optica * moral_actual
            
            st.session_state.g3['fuerzas_propias'].append({
                'Elemento': elemento_nombre, 'VRC': round(vrc_final, 2),
                'Base': round(vrc_base, 2), 'Luz': condicion_luz,
                'Moral G1': moral_actual, 'Fases': fases_op
            })
            
    if st.session_state.g3['fuerzas_propias']:
        st.dataframe(pd.DataFrame(st.session_state.g3['fuerzas_propias']), use_container_width=True)

# ----------------- PANEL G4 -----------------
elif rol == "G4 - Materiales":
    st.header("G4: Sostenimiento y Restricciones Logísticas")
    st.session_state.g4['clase_i'] = st.slider("Clase I (Racionamiento) %", 0, 100, st.session_state.g4.get('clase_i', 100))
    st.session_state.g4['clase_iii'] = st.slider("Clase III (Combustibles y Lubricantes) %", 0, 100, st.session_state.g4.get('clase_iii', 100))
    st.session_state.g4['clase_v'] = st.slider("Clase V (Munición) %", 0, 100, st.session_state.g4.get('clase_v', 100))
    st.session_state.g4['vehiculos_servicio'] = st.slider("Vehículos en Servicio %", 0, 100, st.session_state.g4.get('vehiculos_servicio', 100))

# ----------------- PANEL JEFE PLANA MAYOR -----------------
elif rol == "Jefe de la Plana Mayor":
    st.header("Jefe de la Plana Mayor: Sincronización y Control")
    
    st.subheader("1. Estado Actual de la Plana Mayor")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Moral (G1)", st.session_state.get('g1', {}).get('moral', 'S/D'))
    col_s2.metric("VRC Enemigo (G2)", sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', [])))
    col_s3.metric("VRC Propio (G3)", sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', [])))
    col_s4.metric("Munición (G4)", f"{st.session_state.get('g4', {}).get('clase_v', 0)}%")
    
    st.divider()
    st.subheader("2. Guía del Proceso de Planificación de Comando (PPC)")
    st.info("""
    * **Análisis de la misión:** Identificación del problema.
    * **Reunión de información:** Exposiciones preliminares.
    * **Orientación:** Directivas iniciales del Comandante.
    * **Análisis de la situación:** Determinación de factores de fuerza y debilidad.
    * **Elaboración de MMACC:** Modos de acción propios y capacidades del enemigo.
    * **Confrontación:** Prueba de factibilidad y aceptabilidad inicial.
    * **Comparación:** Determinación de ventajas, desventajas y riesgos.
    * **Resolución:** Enunciado del plan general.
    """)
    
    st.subheader("3. Cronograma de Actividades")
    if 'cronograma' not in st.session_state:
        st.session_state.cronograma = pd.DataFrame(
            columns=["Actividad", "Responsable", "Hora Límite", "Completado"],
            # Corrección: Se utiliza None en lugar de "" para evitar la incompatibilidad de formato
            data=[["", "", None, False] for _ in range(5)]
        )
    
    cronograma_actualizado = st.data_editor(
        st.session_state.cronograma, num_rows="dynamic", use_container_width=True,
        column_config={"Completado": st.column_config.CheckboxColumn("Completado", default=False),
                       "Hora Límite": st.column_config.TimeColumn("Hora Límite", format="HH:mm")}
    )
    st.session_state.cronograma = cronograma_actualizado
    
    st.subheader("4. Evolución del Planeamiento")
    df_valido = cronograma_actualizado[cronograma_actualizado["Actividad"].str.strip() != ""]
    if not df_valido.empty:
        total_tareas = len(df_valido)
        tareas_completadas = df_valido["Completado"].sum()
        porcentaje_avance = (tareas_completadas / total_tareas) * 100
        st.progress(int(porcentaje_avance), text=f"Avance del Planeamiento: {int(porcentaje_avance)}%")
        
        resumen_responsables = df_valido.groupby(["Responsable", "Completado"]).size().unstack(fill_value=0)
        if True not in resumen_responsables: resumen_responsables[True] = 0
        if False not in resumen_responsables: resumen_responsables[False] = 0
        resumen_responsables.rename(columns={True: "Finalizado", False: "Pendiente"}, inplace=True)
        st.bar_chart(resumen_responsables, color=["#ff4b4b", "#00cc96"])

# ----------------- PANEL COMANDANTE -----------------
elif rol == "Comandante":
    st.header("Tablero de Comando y Resolución")
    
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', []))
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', []))
    
    poder_propio = vrc_base_propio * st.session_state.g1.get('moral', 1.0) * st.session_state.g2.get('terreno', 1.0)
    poder_eno = vrc_base_eno * st.session_state.g2.get('terreno', 1.0)
    
    pcr_real = poder_propio / poder_eno if poder_eno > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Poder de Combate Propio", f"{poder_propio:.2f}")
    col2.metric("Poder de Combate Eno", f"{poder_eno:.2f}")
    col3.metric("PCR RESULTANTE", f"{pcr_real:.2f} : 1")
    
    exigencia_pcr = st.session_state.g3.get('pcr_requerido', 1.0)
    alerta_logistica = any(val < 50 for val in st.session_state.get('g4', {'a':100}).values())
    
    if pcr_real >= exigencia_pcr and not alerta_logistica:
        st.success(f"✅ FACTIBLE: El PCR actual ({pcr_real:.2f}) es suficiente para la operación (Requiere {exigencia_pcr}).")
    else:
        st.error(f"⚠️ RIESGO MATEMÁTICO: El PCR de {pcr_real:.2f} es inferior al umbral doctrinario de {exigencia_pcr}.")
    if alerta_logistica:
        st.warning("⚠️ ALERTA LOGÍSTICA: Parámetros de G4 críticos.")

# ----------------- PANEL GESTIÓN DE DATOS -----------------
elif rol == "Gestión de Datos":
    st.header("Gestión del Monitor")
    st.markdown("Elimina todas las unidades cargadas y restablece los parámetros a sus valores nominales.")
    if st.button("⚠️ Limpiar Tablero de Comando", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
