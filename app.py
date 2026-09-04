import streamlit as st
import pandas as pd
import datetime
import numpy as np

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
   
    st.divider()
    st.subheader("4. Proyección Predictiva de Desgaste")
    st.markdown("Cálculo estadístico de bajas según tipo de operación (ROD-71-01-II, Tabla VIII)[cite: 1]")
    
    op_futura = st.selectbox("Operación Planificada", ["Ataque Ruptura", "Ataque Frontal", "Infiltración", "Avance para tomar contacto"])
    degradacion_dict = {"Ataque Ruptura": 0.20, "Ataque Frontal": 0.15, "Infiltración": 0.03, "Avance para tomar contacto": 0.03}
    
    tasa_bajas = degradacion_dict[op_futura]
    bajas_proyectadas = int(efectivos_reales * tasa_bajas)
    efectivos_residuales = efectivos_reales - bajas_proyectadas
    
    st.metric("Efectivos Residuales Proyectados (Post-Operación)", f"{efectivos_residuales}", f"-{bajas_proyectadas} bajas estimadas", delta_color="inverse")
    
    chart_data = pd.DataFrame({
        "Estado": ["Fuerza Inicial", "Bajas Proyectadas", "Fuerza Residual"],
        "Efectivos": [efectivos_reales, bajas_proyectadas, efectivos_residuales]
    })
    st.bar_chart(chart_data.set_index("Estado"))

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
    st.header("G4: Sostenimiento, Munición y Restricciones Logísticas")
    
    # Inicializar bases de datos logísticas
    if 'vehiculos' not in st.session_state.g4:
        st.session_state.g4['vehiculos'] = []
    if 'municion' not in st.session_state.g4:
        st.session_state.g4['municion'] = []
        
    st.subheader("1. Vehículos de Dotación")
    with st.form("form_veh"):
        v_nombre = st.text_input("Modelo de Vehículo (Ej: MB 230G, VCTP)")
        c1, c2, c3 = st.columns(3)
        with c1:
            v_cant = st.number_input("Cantidad", min_value=1, value=5)
            v_auto = st.number_input("Autonomía (Km)", min_value=1.0, value=400.0)
        with c2:
            v_comb = st.selectbox("Combustible", ["Gasoil", "Nafta", "JP-8"])
            v_cons = st.number_input("Consumo c/ 100km (Lts)", min_value=1.0, value=20.0)
        with c3:
            v_lub = st.selectbox("Lubricante principal", ["15W40", "Grasa de Litio", "Transmisión"])
            
        if st.form_submit_button("Cargar Lote de Vehículos") and v_nombre:
            st.session_state.g4['vehiculos'].append({
                "Modelo": v_nombre, "Cant": v_cant, "Autonomía": v_auto,
                "Combustible": v_comb, "Lts/100km": v_cons, "Lubricante": v_lub
            })
            
    if st.session_state.g4['vehiculos']:
        st.dataframe(pd.DataFrame(st.session_state.g4['vehiculos']), use_container_width=True)
        
    st.divider()
    st.subheader("2. Stock General y Munición")
    c_st1, c_st2 = st.columns(2)
    with c_st1:
        st.session_state.g4['stock_combustible'] = st.number_input("Stock Total Combustible (Lts)", min_value=0, value=10000)
    with c_st2:
        st.session_state.g4['stock_lubricante'] = st.number_input("Stock Total Lubricantes (Lts/Kg)", min_value=0, value=500)
        
    with st.form("form_mun"):
        m_tipo = st.text_input("Calibre / Tipo de Munición (Ej: 7.62x51mm, 105mm)")
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            m_rep = st.number_input("Cantidad Repartida (En tropas)", min_value=0, value=2000)
        with c_m2:
            m_stock = st.number_input("Cantidad en Stock (Polvorín)", min_value=0, value=8000)
            
        if st.form_submit_button("Cargar Munición") and m_tipo:
            st.session_state.g4['municion'].append({
                "Tipo/Calibre": m_tipo, "Repartida": m_rep, "En Stock": m_stock, "Total General": m_rep + m_stock
            })
            
    if st.session_state.g4['municion']:
        st.dataframe(pd.DataFrame(st.session_state.g4['municion']), use_container_width=True)
        
    st.divider()
    st.subheader("3. Proyección del Punto de Culminación (Combustible)")
    distancia_op = st.number_input("Distancia de Penetración Planificada (Km)", min_value=1.0, value=100.0)
    
    if st.session_state.g4['vehiculos']:
        consumo_km = sum((v['Lts/100km'] / 100) * v['Cant'] for v in st.session_state.g4['vehiculos'])
        stock_actual = st.session_state.g4['stock_combustible']
        
        # Calcular en qué kilómetro exacto se agota el combustible
        km_culminacion = stock_actual / consumo_km if consumo_km > 0 else 0
        
        c_cul1, c_cul2 = st.columns(2)
        c_cul1.metric("Consumo Promedio de la Columna", f"{consumo_km:.2f} Lts/Km")
        
        if km_culminacion < distancia_op:
            c_cul2.metric("Punto de Culminación Logística", f"Km {km_culminacion:.1f}", "¡Impulso perdido antes del objetivo!", delta_color="inverse")
            st.error(f"⚠️ La fuerza se detendrá a los {km_culminacion:.1f} Km por falta de combustible.")
        else:
            c_cul2.metric("Punto de Culminación Logística", f"Km {km_culminacion:.1f}", "Stock suficiente para el objetivo")
            st.success("✅ Autonomía logística garantizada para la distancia de la operación.")
            
    st.divider()
    st.subheader("4. Disponibilidad y Aporte al PCR")
    st.session_state.g4['vehiculos_servicio'] = st.slider("Porcentaje de Vehículos en Servicio", 0, 100, 100)
    mod_g4 = st.session_state.g4['vehiculos_servicio'] / 100.0
    st.info(f"Multiplicador Logístico: x{mod_g4:.2f} (Impactará directamente en la capacidad de combate del Comandante).")
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
    * **Análisis de la misión:** Identificación del problema[cite: 1].
    * **Reunión de información:** Exposiciones preliminares[cite: 1].
    * **Orientación:** Directivas iniciales del Comandante[cite: 1].
    * **Análisis de la situación:** Determinación de factores de fuerza y debilidad[cite: 1].
    * **Elaboración de MMACC:** Modos de acción propios y capacidades del enemigo[cite: 1].
    * **Confrontación:** Prueba de factibilidad y aceptabilidad inicial[cite: 1].
    * **Comparación:** Determinación de ventajas, desventajas y riesgos[cite: 1].
    * **Resolución:** Enunciado del plan general[cite: 1].
    """)
    
    st.subheader("3. Cronograma de Actividades")
    if 'cronograma' not in st.session_state:
        # Se inicializa con strings vacíos para permitir carga 100% manual
        st.session_state.cronograma = pd.DataFrame(
            columns=["Actividad", "Responsable", "Hora", "Completado"],
            data=[["", "", "", False] for _ in range(5)]
        )
    
    # Editor nativo sin forzar formatos de tiempo
    cronograma_actualizado = st.data_editor(
        st.session_state.cronograma, 
        num_rows="dynamic", 
        use_container_width=True,
        hide_index=True
    )
    st.session_state.cronograma = cronograma_actualizado
    
    st.subheader("4. Evolución del Planeamiento")
    df_valido = cronograma_actualizado[cronograma_actualizado["Actividad"].str.strip() != ""]
    
    if not df_valido.empty:
        total_tareas = len(df_valido)
        tareas_completadas = df_valido["Completado"].sum()
        porcentaje_avance = (tareas_completadas / total_tareas) * 100
        
        # Única barra de progreso visual
        st.progress(int(porcentaje_avance), text=f"Avance del Planeamiento: {int(porcentaje_avance)}%")
    else:
        st.warning("Comience a cargar actividades en el cronograma para visualizar la evolución.")

# ----------------- PANEL COMANDANTE -----------------
elif rol == "Comandante":
    st.header("Tablero de Comando y Resolución")
    
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', []))
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', []))
    
    # Factores multiplicadores consolidados de la Plana Mayor
    mod_g1_moral = st.session_state.g1.get('moral', 1.0)
    mod_g2_terreno = st.session_state.g2.get('terreno', 1.0)
    mod_g4_logistico = st.session_state.g4.get('vehiculos_servicio', 100) / 100.0
    
    # Cálculo Integrado del Poder de Combate Relativo (PCR)
    poder_propio = vrc_base_propio * mod_g1_moral * mod_g2_terreno * mod_g4_logistico
    poder_eno = vrc_base_eno * mod_g2_terreno
    
    pcr_real = poder_propio / poder_eno if poder_eno > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Poder de Combate Propio (Ajustado)", f"{poder_propio:.2f}")
    col2.metric("Poder de Combate Eno (Ajustado)", f"{poder_eno:.2f}")
    col3.metric("PCR RESULTANTE", f"{pcr_real:.2f} : 1")
    
    exigencia_pcr = st.session_state.g3.get('pcr_requerido', 1.0)
    
    if pcr_real >= exigencia_pcr:
        st.success(f"✅ FACTIBLE: El PCR actual ({pcr_real:.2f}) supera la exigencia doctrinaria para la operación (Requiere {exigencia_pcr}).")
    else:
        st.error(f"⚠️ RIESGO TÁCTICO INACEPTABLE: El PCR de {pcr_real:.2f} es inferior al umbral doctrinario de {exigencia_pcr}.")
        
    if st.session_state.g4.get('vehiculos_servicio', 100) < 60:
        st.warning("⚠️ ALERTA LOGÍSTICA (G4): La tasa de vehículos en servicio es crítica, amenazando la movilidad de la operación.")
        st.divider()
    st.subheader("Análisis de Sensibilidad de Riesgo (What-If)")
    st.markdown("Mapa de calor del PCR proyectando fluctuaciones en Logística y Moral.")
    
    # Generar matriz cruzada (Moral vs Vehículos en Servicio)
    valores_moral = [0.5, 1.0, 1.5, 2.0]  # Baja, Normal, Alta, Muy Alta
    valores_logistica = [0.4, 0.6, 0.8, 1.0] # 40%, 60%, 80%, 100% en servicio
    
    matriz_pcr = np.zeros((len(valores_moral), len(valores_logistica)))
    
    for i, m in enumerate(valores_moral):
        for j, log in enumerate(valores_logistica):
            # Recalcular PCR para cada escenario
            p_propio_sim = vrc_base_propio * m * mod_g2_terreno * log
            matriz_pcr[i, j] = p_propio_sim / poder_eno if poder_eno > 0 else 0
            
    df_sensibilidad = pd.DataFrame(
        matriz_pcr, 
        index=["Moral Baja", "Moral Normal", "Moral Alta", "Moral Muy Alta"],
        columns=["Log 40%", "Log 60%", "Log 80%", "Log 100%"]
    )
    
   # Renderizar matriz de sensibilidad sin depender de matplotlib
    st.dataframe(
        df_sensibilidad.style.format("{:.2f}"),
        use_container_width=True
    )
    st.caption(f"El umbral requerido para el éxito actual es {exigencia_pcr}:1.")

# ----------------- PANEL CONFRONTACIÓN (JUEGO DE GUERRA) -----------------
elif rol == "Confrontación (Juego de Guerra)":
    st.header("Matriz de Confrontación Automatizada")
    st.markdown("Simulación de incidentes y cálculo de degradación residual (ROD-71-01-II, Anexo 3 y 8)[cite: 1].")
    
    # Inicializar registro de confrontación
    if 'log_confrontacion' not in st.session_state:
        st.session_state.log_confrontacion = []
        
    # Obtener VRC iniciales de las sesiones G2 y G3
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', []))
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', []))
    
    # Calcular VRC residual basado en el historial de incidentes
    vrc_residual_propio = vrc_base_propio
    vrc_residual_eno = vrc_base_eno
    
    for choque in st.session_state.log_confrontacion:
        vrc_residual_propio -= (vrc_residual_propio * (choque['Degradación G3 %'] / 100))
        vrc_residual_eno -= (vrc_residual_eno * (choque['Degradación G2 %'] / 100))
        
    c1, c2, c3 = st.columns(3)
    c1.metric("VRC Propio (Disponible)", f"{vrc_residual_propio:.2f}", f"Inicial: {vrc_base_propio:.2f}")
    c2.metric("VRC Enemigo (Disponible)", f"{vrc_residual_eno:.2f}", f"Inicial: {vrc_base_eno:.2f}")
    c3.metric("PCR Local", f"{(vrc_residual_propio / vrc_residual_eno if vrc_residual_eno > 0 else 0):.2f} : 1")
    
    st.divider()
    
    **Registro de Nuevo Incidente Táctico**
    with st.form("form_incidente"):
        fase_incidente = st.text_input("Etapa / Incidente (Ej: Franquear Río Blanco)")
        
        col_g3, col_g2 = st.columns(2)
        with col_g3:
            accion_g3 = st.text_area("Acción G3 (Azul)", placeholder="Ej: Ataque frontal con 1 Ca I Mec...")
            deg_g3 = st.number_input("Degradación Estimada Propia (%)", min_value=0, max_value=100, value=15)
            
        with col_g2:
            reaccion_g2 = st.text_area("Reacción G2 (Colorado)", placeholder="Ej: Fuego de contrapreparación...")
            deg_g2 = st.number_input("Degradación Estimada Enemiga (%)", min_value=0, max_value=100, value=10)
            
        if st.form_submit_button("Resolver Incidente y Aplicar Fricción"):
            if fase_incidente:
                st.session_state.log_confrontacion.append({
                    "Incidente": fase_incidente,
                    "Acción (G3)": accion_g3,
                    "Reacción (G2)": reaccion_g2,
                    "Degradación G3 %": deg_g3,
                    "Degradación G2 %": deg_g2
                })
                st.rerun()

    **Historial de la Maniobra**
    if st.session_state.log_confrontacion:
        st.dataframe(pd.DataFrame(st.session_state.log_confrontacion), use_container_width=True)
        
        if st.button("Deshacer último incidente"):
            st.session_state.log_confrontacion.pop()
            st.rerun()

# ----------------- PANEL GESTIÓN DE DATOS -----------------
elif rol == "Gestión de Datos":
    st.header("Gestión del Monitor")
    st.markdown("Elimina todas las unidades cargadas y restablece los parámetros a sus valores nominales.")
    if st.button("⚠️ Limpiar Tablero de Comando", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
