import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

st.set_page_config(page_title="Monitor C2 - Riesgo Cuantitativo", layout="wide")

if 'g1' not in st.session_state:
    st.session_state.g1 = {'experiencia': 1.0, 'personal_permanente': 1.0, 'moral': 1.0}
if 'g2' not in st.session_state:
    st.session_state.g2 = {'terreno': 1.0, 'clima': 1.0, 'fuerzas_eno': [], 'ambiente': 'Llanura'}
if 'g3' not in st.session_state:
    st.session_state.g3 = {'fuerzas_propias': [], 'tipo_operacion': 'Ataque Frontal', 'pcr_requerido': 3.0}
if 'g4' not in st.session_state:
    st.session_state.g4 = {'clase_i': 100, 'clase_iii': 100, 'clase_v': 100, 'vehiculos_servicio': 100, 'vehiculos': [], 'municion': [], 'stock_combustible': 10000}

st.sidebar.title("Áreas de Conducción")
rol = st.sidebar.radio("Seleccione Panel:", [
    "G1 - Personal", "G2 - Inteligencia", "G3 - Operaciones", "G4 - Materiales", 
    "Confrontación (Monte Carlo)", "Jefe de la Plana Mayor", "Comandante", "Gestión de Datos"
])

# ----------------- PANEL G1 -----------------
if rol == "G1 - Personal":
    st.header("G1: Carga Manual y Cálculo Analítico de Personal")
    
    col1, col2 = st.columns(2)
    with col1:
        total_efectivos = st.number_input("Total de Efectivos", min_value=1, value=100)
    with col2:
        exp_combate = st.number_input("Personal con Experiencia en Combate", min_value=0, max_value=total_efectivos, value=0)
    
    niveles = {"Alta instrucción": 1.0, "Mediana instrucción": 0.75, "Baja instrucción": 0.5}
    col_of, col_subof, col_sold = st.columns(3)
    with col_of:
        inst_of = st.selectbox("Oficiales", list(niveles.keys()), index=0)
    with col_subof:
        inst_subof = st.selectbox("Suboficiales", list(niveles.keys()), index=0)
    with col_sold:
        inst_sold = st.selectbox("Soldados", list(niveles.keys()), index=1)
        
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
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Efectivos en Condiciones", f"{efectivos_reales}", f"-{bajas_totales} bajas")
    rc2.metric("Estado Moral Calculado", moral_text, f"Multiplicador: {moral_calc}")
    rc3.metric("Capacidad de Combate", f"{(factor_exp * factor_instruccion * moral_calc):.2f}")

# ----------------- PANEL G2 -----------------
elif rol == "G2 - Inteligencia":
    st.header("G2: Ambiente Geográfico y Orden de Batalla Enemigo")
    
    st.session_state.g2['ambiente'] = st.selectbox("Ambiente Geográfico", ["Insular", "Desértico", "Desértico Patagónico", "Montaña", "Monte", "Llanura", "Urbano"])
    mod_terreno = {"Favorable": 1.2, "Limitado": 0.8, "Desfavorable": 0.5}
    st.session_state.g2['terreno'] = mod_terreno[st.selectbox("Aptitud del Terreno (Eno)", list(mod_terreno.keys()))]
    
    st.divider()
    with st.form("form_eno_avanzado"):
        tipo_eno = st.text_input("Denominación del Elemento (Ej: Batallón de Infantería Enemigo)")
        col_fza, col_alc = st.columns(2)
        with col_fza:
            efectivos_pie = st.number_input("Número Relativo de Fuerzas a Pie", min_value=0, value=100)
            autonomia = st.number_input("Autonomía Operativa (Km)", min_value=0.0, value=50.0, step=10.0)
        with col_alc:
            alcance_armas = st.number_input("Alcance Promedio Armas (Km)", min_value=0.0, value=2.0, step=0.1)
            
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1: has_drones = st.checkbox("Sistemas Drones / UAS")
        with col_t2: has_nocturna = st.checkbox("Capacidad Nocturna Estándar")
        with col_t3: has_termografica = st.checkbox("Visión Termográfica Avanzada")
            
        if st.form_submit_button("Calcular VRC y Cargar al Tablero") and tipo_eno:
            vrc_base = (efectivos_pie * 0.01) + (alcance_armas * 0.15) + (autonomia * 0.005)
            vrc_calculado = vrc_base * (1.25 if has_drones else 1.0) * (1.35 if has_termografica else (1.15 if has_nocturna else 1.0))
            st.session_state.g2['fuerzas_eno'].append({'Elemento': tipo_eno, 'VRC': round(vrc_calculado, 2)})
            
    if st.session_state.g2['fuerzas_eno']:
        st.dataframe(pd.DataFrame(st.session_state.g2['fuerzas_eno']), use_container_width=True)

# ----------------- PANEL G3 -----------------
elif rol == "G3 - Operaciones":
    st.header("G3: Maniobra, Exploración y Poder de Combate Propio")
    
    tipo_op_principal = st.selectbox("Clasificación de la Operación", ["Ofensiva", "Defensiva", "Complementaria"])
    ops_dict = {
        "Ofensiva": ["Ataque Ruptura (5:1)", "Ataque Frontal (3:1)", "Ataque Envolvente", "Explotación"],
        "Defensiva": ["Defensa de Zona (0.33:1)", "Defensa Móvil", "Acción Retardante"],
        "Complementaria": ["Exploración", "Seguridad", "Marcha de Aproximación", "Infiltración"]
    }
    op_detallada = st.selectbox("Tipo", ops_dict[tipo_op_principal])
    st.session_state.g3['tipo_operacion'] = op_detallada.split(" ")[0]
    st.session_state.g3['pcr_requerido'] = float(op_detallada.split("(")[1].split(":")[0]) if "(" in op_detallada else 1.0
        
    st.divider()
    with st.form("form_op_propia"):
        elemento_nombre = st.text_input("Unidad / Fracción a emplear")
        col_amb, col_luz = st.columns(2)
        with col_amb: ambiente = st.selectbox("Ambiente Geográfico", ["Insular", "Desértico", "Montaña", "Monte", "Llanura", "Urbano"], index=4)
        with col_luz: condicion_luz = st.selectbox("Condición de Iluminación", ["Diurna", "Nocturna"])
            
        col_p, col_a, col_v = st.columns(3)
        with col_p: efectivos = st.number_input("Personal Empleado", min_value=1, value=50)
        with col_a: alcance = st.number_input("Alcance Promedio Armamento (Km)", min_value=0.0, value=2.5, step=0.1)
        with col_v: autonomia = st.number_input("Autonomía Vehículos (Km)", min_value=0.0, value=300.0, step=10.0)
            
        col_v1, col_v2 = st.columns(2)
        with col_v1: vn_estandar = st.checkbox("Visión Nocturna")
        with col_v2: vn_termo = st.checkbox("Visión Termográfica")
        
        if st.form_submit_button("Calcular PCR y Asignar") and elemento_nombre:
            vrc_base = (efectivos * 0.01) + (alcance * 0.15) + (autonomia * 0.005)
            mod_optica = 1.5 if vn_termo else (1.0 if vn_estandar else 0.5) if condicion_luz == "Nocturna" else 1.0
            vrc_final = vrc_base * mod_optica * st.session_state.g1.get('moral', 1.0)
            
            st.session_state.g3['fuerzas_propias'].append({'Elemento': elemento_nombre, 'VRC': round(vrc_final, 2)})
            
    if st.session_state.g3['fuerzas_propias']:
        st.dataframe(pd.DataFrame(st.session_state.g3['fuerzas_propias']), use_container_width=True)

# ----------------- PANEL G4 -----------------
elif rol == "G4 - Materiales":
    st.header("G4: Sostenimiento, Munición y Restricciones Logísticas")
    
    with st.form("form_veh"):
        v_nombre = st.text_input("Modelo de Vehículo")
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
            st.session_state.g4['vehiculos'].append({"Modelo": v_nombre, "Cant": v_cant, "Consumo_100": v_cons})
            
    if st.session_state.g4['vehiculos']:
        st.dataframe(pd.DataFrame(st.session_state.g4['vehiculos']), use_container_width=True)
        
    st.session_state.g4['stock_combustible'] = st.number_input("Stock Total Combustible (Lts)", min_value=0, value=10000)
    st.session_state.g4['vehiculos_servicio'] = st.slider("Vehículos en Servicio %", 0, 100, st.session_state.g4.get('vehiculos_servicio', 100))

# ----------------- PANEL CONFRONTACIÓN -----------------
elif rol == "Confrontación (Monte Carlo)":
    st.header("Matriz de Confrontación Estocástica")
    st.markdown("Simulación probabilística de incidentes y cálculo iterativo (ROD-71-01-II, Anexo 3)[cite: 1].")
    
    if 'log_confrontacion' not in st.session_state:
        st.session_state.log_confrontacion = []
        
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', []))
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', []))
    
    with st.form("form_incidente"):
        fase_incidente = st.text_input("Incidente Táctico")
        col_g3, col_g2 = st.columns(2)
        with col_g3:
            deg_g3_min = st.number_input("Degradación Propia Mín (%)", min_value=0, max_value=100, value=10)
            deg_g3_max = st.number_input("Degradación Propia Máx (%)", min_value=0, max_value=100, value=25)
        with col_g2:
            deg_g2_min = st.number_input("Degradación Eno Mín (%)", min_value=0, max_value=100, value=5)
            deg_g2_max = st.number_input("Degradación Eno Máx (%)", min_value=0, max_value=100, value=15)
            
        if st.form_submit_button("Ejecutar Simulación Monte Carlo (1000 iteraciones)"):
            sim_g3 = np.random.uniform(deg_g3_min, deg_g3_max, 1000) / 100
            sim_g2 = np.random.uniform(deg_g2_min, deg_g2_max, 1000) / 100
            
            pcr_req = st.session_state.g3.get('pcr_requerido', 1.0)
            vrc_prop_sim = vrc_base_propio * (1 - sim_g3)
            vrc_eno_sim = vrc_base_eno * (1 - sim_g2)
            pcr_sim = np.divide(vrc_prop_sim, vrc_eno_sim, out=np.zeros_like(vrc_prop_sim), where=vrc_eno_sim!=0)
            
            prob_exito = np.mean(pcr_sim >= pcr_req) * 100
            
            st.session_state.log_confrontacion.append({
                "Incidente": fase_incidente, 
                "Probabilidad Éxito (%)": prob_exito,
                "Degradación Promedio Propia (%)": np.mean(sim_g3)*100
            })
            st.rerun()

    if st.session_state.log_confrontacion:
        st.dataframe(pd.DataFrame(st.session_state.log_confrontacion), use_container_width=True)

# ----------------- PANEL JEFE PLANA MAYOR -----------------
elif rol == "Jefe de la Plana Mayor":
    st.header("Sincronización Espacio-Tiempo (Diagrama de Gantt)")
    
    if 'cronograma' not in st.session_state:
        # Se estructura con Fechas para permitir el diagrama
        st.session_state.cronograma = pd.DataFrame(
            columns=["Actividad", "Responsable", "Inicio", "Fin", "Completado"],
            data=[
                ["Análisis de la misión", "J Pl My", "2026-10-01 08:00", "2026-10-01 10:00", False],
                ["Apreciación Inteligencia", "G2", "2026-10-01 10:00", "2026-10-01 12:00", False],
                ["", "", "", "", False]
            ]
        )
    
    df_actualizado = st.data_editor(st.session_state.cronograma, num_rows="dynamic", use_container_width=True)
    st.session_state.cronograma = df_actualizado
    
    df_valido = df_actualizado[(df_actualizado["Actividad"].str.strip() != "") & (df_actualizado["Inicio"].str.strip() != "") & (df_actualizado["Fin"].str.strip() != "")]
    
    if not df_valido.empty:
        try:
            df_valido['Inicio'] = pd.to_datetime(df_valido['Inicio'])
            df_valido['Fin'] = pd.to_datetime(df_valido['Fin'])
            
            # Gráfico de Gantt nativo con Altair (No requiere requirements.txt)
            gantt = alt.Chart(df_valido).mark_bar().encode(
                x=alt.X('Inicio:T', title='Horario de Inicio'),
                x2='Fin:T',
                y=alt.Y('Actividad:N', sort='x', title='Actividades del PPC'),
                color=alt.Color('Responsable:N', legend=alt.Legend(title="Área")),
                tooltip=['Actividad', 'Responsable', 'Inicio', 'Fin']
            ).properties(
                title='Sincronización de la Maniobra',
                height=350
            ).interactive()
            
            st.altair_chart(gantt, use_container_width=True)
            
        except Exception as e:
            st.warning("Formato de fecha inválido. Utilice el formato 'YYYY-MM-DD HH:MM' (Ej: 2026-10-01 08:00).")

# ----------------- PANEL COMANDANTE -----------------
elif rol == "Comandante":
    st.header("Tablero de Resolución Cuantitativa")
    
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.get('g3', {}).get('fuerzas_propias', []))
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.get('g2', {}).get('fuerzas_eno', []))
    
    poder_propio = vrc_base_propio * st.session_state.g1.get('moral', 1.0) * st.session_state.g2.get('terreno', 1.0) * (st.session_state.g4.get('vehiculos_servicio', 100) / 100.0)
    poder_eno = vrc_base_eno * st.session_state.g2.get('terreno', 1.0)
    
    pcr_real = poder_propio / poder_eno if poder_eno > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Poder de Combate Propio", f"{poder_propio:.2f}")
    c2.metric("Poder de Combate Eno", f"{poder_eno:.2f}")
    c3.metric("PCR RESULTANTE", f"{pcr_real:.2f} : 1")
    
    st.divider()
    st.subheader("Índice de Eficiencia Táctica (Economía de la Fuerza)")
    # Calcula el costo logístico (consumo proyectado a 100km)
    consumo_km = sum((v['Consumo_100'] / 100) * v['Cant'] for v in st.session_state.g4.get('vehiculos', []))
    costo_logistico_100km = consumo_km * 100
    
    if costo_logistico_100km > 0:
        iet = vrc_base_eno / costo_logistico_100km
        st.metric("Índice de Eficiencia (VRC Destruido / Litros de Combustible)", f"{iet:.4f}", "Valor más alto indica mejor uso de la masa")
    else:
        st.info("Cargue vehículos en G4 para calcular el Índice de Eficiencia Logística.")

# ----------------- PANEL GESTIÓN DE DATOS -----------------
elif rol == "Gestión de Datos":
    st.header("Gestión del Monitor")
    if st.button("⚠️ Limpiar Tablero de Comando", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
