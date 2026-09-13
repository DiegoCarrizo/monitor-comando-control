import streamlit as st
import pandas as pd
import numpy as np
import datetime
import altair as alt

st.set_page_config(page_title="Monitor C2 - Escuadrón", layout="wide")

# Inicialización de bases de datos temporales (Doctrina Unidad/Subunidad)
if 's1' not in st.session_state:
    st.session_state.s1 = {'experiencia': 1.0, 'moral': 1.0, 'bajas_predictivas': 0}
if 's2' not in st.session_state:
    st.session_state.s2 = {'terreno': 1.0, 'fuerzas_eno': []}
if 's3' not in st.session_state:
    st.session_state.s3 = {'fuerzas_propias': [], 'tipo_operacion': 'Ataque', 'pcr_requerido': 3.0, 'vrc_fuegos': 0, 'reserva': []}
if 's4' not in st.session_state:
    st.session_state.s4 = {
        'stock_combustible': 10000, 'stock_municion': 5000, 'stock_lubricante': 500,
        'asignaciones': [], 'vehiculos_servicio': 100, 'eficiencia_c2': 1.0
    }
import pandas as pd
import numpy as np
import datetime
import altair as alt

st.set_page_config(page_title="Monitor C2 - Escuadrón", layout="wide")

# Inicialización de bases de datos temporales (Doctrina Unidad/Subunidad)
if 's1' not in st.session_state:
    st.session_state.s1 = {'experiencia': 1.0, 'moral': 1.0, 'bajas_predictivas': 0}
if 's2' not in st.session_state:
    st.session_state.s2 = {'terreno': 1.0, 'fuerzas_eno': []}
if 's3' not in st.session_state:
    st.session_state.s3 = {'fuerzas_propias': [], 'tipo_operacion': 'Ataque', 'pcr_requerido': 3.0, 'vrc_fuegos': 0, 'reserva': []}
if 's4' not in st.session_state:
    st.session_state.s4 = {
        'stock_combustible': 10000, 'stock_municion': 5000, 'stock_lubricante': 500,
        'asignaciones': [], 'vehiculos_servicio': 100, 'eficiencia_c2': 1.0
    }

st.sidebar.title("Plana Mayor (Escuadrón)")
rol = st.sidebar.radio("Seleccione Panel:", [
    "S1 - Personal y Sanidad", 
    "S2 - Inteligencia", 
    "S3 - Operaciones y Fuegos", 
    "S4 - Logística y Comunicaciones",
    "Confrontación (Monte Carlo)", 
    "Jefe de la Plana Mayor", 
    "Comandante (Resolución y Reserva)", 
    "Gestión de Datos"
])

# ----------------- PANEL S1 -----------------
if rol == "S1 - Personal y Sanidad":
    st.header("S1: Efectivos, Moral y Sanidad (MEDEVAC)")
    
    col1, col2 = st.columns(2)
    with col1: total_efectivos = st.number_input("Total de Efectivos", min_value=1, value=150)
    with col2: exp_combate = st.number_input("Personal con Experiencia de Combate", min_value=0, max_value=total_efectivos, value=20)
    
    st.subheader("Bajas Actuales")
    cb1, cb2, cb3 = st.columns(3)
    with cb1: muertos = st.number_input("Muertos (KIA)", min_value=0, value=0)
    with cb2: heridos = st.number_input("Heridos (WIA)", min_value=0, value=0)
    with cb3: desaparecidos = st.number_input("Desaparecidos / Evacuados", min_value=0, value=0)
        
    efectivos_reales = total_efectivos - (muertos + heridos + desaparecidos)
    impacto_moral = (heridos + desaparecidos + (muertos * 2)) / total_efectivos if total_efectivos > 0 else 0
        
    moral_calc = 2.0 if impacto_moral == 0 else (1.5 if impacto_moral < 0.05 else (1.0 if impacto_moral < 0.15 else 0.5))
    st.session_state.s1['moral'] = moral_calc
    
    rc1, rc2 = st.columns(2)
    rc1.metric("Efectivos Disponibles", f"{efectivos_reales}", f"-{total_efectivos - efectivos_reales} bajas")
    rc2.metric("Multiplicador Moral", f"x{moral_calc:.2f}")

    st.divider()
    st.subheader("Proyección Predictiva de Desgaste")
    op_futura = st.selectbox("Operación Planificada para S3", ["Ataque Ruptura", "Ataque Frontal", "Exploración", "Defensa"])
    deg_dict = {"Ataque Ruptura": 0.20, "Ataque Frontal": 0.15, "Exploración": 0.05, "Defensa": 0.10}
    
    bajas_proyectadas = int(efectivos_reales * deg_dict[op_futura])
    st.session_state.s1['bajas_predictivas'] = bajas_proyectadas
    st.metric("Bajas Estimadas para la Operación", f"{bajas_proyectadas} efectivos", delta_color="inverse")

    st.divider()
    st.subheader("Sanidad y Evacuación Médica")
    ambulancias = st.number_input("Ambulancias Disponibles (M113 / Unimog)", min_value=0, value=2)
    capacidad_evac = ambulancias * 4 
    
    st.metric("Capacidad de Evacuación Simultánea", f"{capacidad_evac} pacientes")
    if bajas_proyectadas > capacidad_evac:
        st.error(f"⚠️ PELIGRO: Las bajas proyectadas ({bajas_proyectadas}) superan la capacidad de evacuación. El Puesto Socorro colapsará sin apoyo exterior.")
    else:
        st.success("✅ Capacidad MEDEVAC suficiente para la operación planificada.")

# ----------------- PANEL S2 -----------------
elif rol == "S2 - Inteligencia":
    st.header("S2: Entorno y Orden de Batalla Enemigo")
    
    st.session_state.s2['ambiente'] = st.selectbox("Ambiente", ["Llanura", "Monte", "Montaña", "Urbano"])
    mod_terreno = {"Favorable": 1.2, "Limitado": 0.8, "Desfavorable": 0.5}
    st.session_state.s2['terreno'] = mod_terreno[st.selectbox("Aptitud del Terreno (Eno)", list(mod_terreno.keys()))]
    
    st.divider()
    with st.form("form_eno"):
        tipo_eno = st.text_input("Elemento Enemigo Detectado")
        c1, c2 = st.columns(2)
        with c1: efectivos = st.number_input("Fuerza a pie (%)", value=100)
        with c2: alcance = st.number_input("Alcance Armas (Km)", value=2.0)
        
        if st.form_submit_button("Cargar VRC Enemigo") and tipo_eno:
            vrc_base = (efectivos * 0.01) + (alcance * 0.15)
            st.session_state.s2['fuerzas_eno'].append({'Elemento': tipo_eno, 'VRC': round(vrc_base, 2)})
            
    if st.session_state.s2['fuerzas_eno']:
        st.dataframe(pd.DataFrame(st.session_state.s2['fuerzas_eno']), use_container_width=True)

# ----------------- PANEL S3 -----------------
elif rol == "S3 - Operaciones y Fuegos":
    st.header("S3: Maniobra, Reserva y Apoyo de Fuego")
    
    tipo_op = st.selectbox("Clasificación de la Operación", ["Ataque Ruptura (5:1)", "Ataque Frontal (3:1)", "Exploración (1:1)", "Defensa (0.33:1)"])
    st.session_state.s3['tipo_operacion'] = tipo_op.split(" ")[0]
    st.session_state.s3['pcr_requerido'] = float(tipo_op.split("(")[1].split(":")[0])
        
    with st.form("form_op_propia"):
        elemento = st.text_input("Elemento Principal a Emplear (Ej: 1ra Sección Bl)")
        c1, c2 = st.columns(2)
        with c1: efectivos = st.number_input("Efectivos", min_value=1, value=30)
        with c2: alcance = st.number_input("Alcance (Km)", value=2.5)
        vn_termo = st.checkbox("Visión Termográfica")
        
        if st.form_submit_button("Asignar Elemento Principal") and elemento:
            vrc_f = ((efectivos * 0.01) + (alcance * 0.15)) * (1.5 if vn_termo else 1.0) * st.session_state.s1.get('moral', 1.0)
            st.session_state.s3['fuerzas_propias'].append({'Elemento': elemento, 'VRC': round(vrc_f, 2)})
            
    if st.session_state.s3['fuerzas_propias']:
        st.dataframe(pd.DataFrame(st.session_state.s3['fuerzas_propias']), use_container_width=True)

    st.divider()
    st.subheader("Asignación de Elemento en Reserva")
    with st.form("form_reserva"):
        elem_res = st.text_input("Fracción en Reserva (Ej: 2da Sección Bl / Exploración)")
        vrc_res = st.number_input("Valor Relativo de Combate (VRC) de la Reserva", min_value=0.1, value=1.5, step=0.1)
        
        if st.form_submit_button("Constituir Reserva") and elem_res:
            st.session_state.s3['reserva'] = [{'Elemento': elem_res, 'VRC': round(vrc_res, 2), 'Empeñada': False}]
            
    if st.session_state.s3['reserva']:
        st.dataframe(pd.DataFrame(st.session_state.s3['reserva']), use_container_width=True)

    st.divider()
    st.subheader("Centro Coordinador de Apoyo de Fuego")
    morteros = st.checkbox("Apoyo de Morteros Pesados (120mm) Disponible")
    if morteros:
        disp_humo = st.slider("Disponibilidad Munición Especial (Humo/Iluminación) %", 0, 100, 50)
        st.session_state.s3['vrc_fuegos'] = 1.5 + (disp_humo * 0.01)
        st.success(f"Fuegos integrados. Bono VRC de Apoyo: +{st.session_state.s3['vrc_fuegos']:.2f}")
    else:
        st.session_state.s3['vrc_fuegos'] = 0

# ----------------- PANEL S4 -----------------
elif rol == "S4 - Logística y Comunicaciones":
    st.header("S4: Sostenimiento, Abastecimiento y Comunicaciones")
    
    if 'asignaciones' not in st.session_state.s4:
        st.session_state.s4['asignaciones'] = []
    
    st.subheader("1. Stock General del Escuadrón (Tren Logístico)")
    c1, c2, c3 = st.columns(3)
    st.session_state.s4['stock_combustible'] = c1.number_input("Combustible Existente (Lts)", min_value=0, value=st.session_state.s4.get('stock_combustible', 10000))
    st.session_state.s4['stock_municion'] = c2.number_input("Munición Existente (Tiros)", min_value=0, value=st.session_state.s4.get('stock_municion', 5000))
    st.session_state.s4['stock_lubricante'] = c3.number_input("Lubricante Existente (Kg/Lts)", min_value=0, value=st.session_state.s4.get('stock_lubricante', 500))

    st.divider()
    st.subheader("2. Asignación de Efectos a Subunidades")
    with st.form("form_asignacion"):
        elem_asig = st.text_input("Elemento a Abastecer (Ej: 1ra Sección Bl)")
        ca1, ca2, ca3 = st.columns(3)
        with ca1: asig_comb = st.number_input("Clase III - Combustible (Lts)", min_value=0, value=0)
        with ca2: asig_mun = st.number_input("Clase V - Munición (Tiros)", min_value=0, value=0)
        with ca3: asig_lub = st.number_input("Clase III - Lubricantes", min_value=0, value=0)
        
        if st.form_submit_button("Entregar Material") and elem_asig:
            st.session_state.s4['asignaciones'].append({
                "Elemento": elem_asig, "Combustible": asig_comb, "Munición": asig_mun, "Lubricante": asig_lub
            })

    tot_comb = sum(item["Combustible"] for item in st.session_state.s4['asignaciones'])
    tot_mun = sum(item["Munición"] for item in st.session_state.s4['asignaciones'])
    tot_lub = sum(item["Lubricante"] for item in st.session_state.s4['asignaciones'])

    rest_comb = st.session_state.s4['stock_combustible'] - tot_comb
    rest_mun = st.session_state.s4['stock_municion'] - tot_mun
    rest_lub = st.session_state.s4['stock_lubricante'] - tot_lub

    st.subheader("3. Saldos Logísticos (Disponibilidad Real)")
    cr1, cr2, cr3 = st.columns(3)
    cr1.metric("Combustible Restante", f"{rest_comb} Lts", f"-{tot_comb} asignados", delta_color="inverse")
    cr2.metric("Munición Restante", f"{rest_mun} Tiros", f"-{tot_mun} asignados", delta_color="inverse")
    cr3.metric("Lubricante Restante", f"{rest_lub}", f"-{tot_lub} asignados", delta_color="inverse")
    
    if rest_comb < 0 or rest_mun < 0 or rest_lub < 0:
        st.error("⚠️ ALERTA LOGÍSTICA: Las asignaciones actuales superan el stock general. Quiebre de abastecimiento inminente.")

    if st.session_state.s4['asignaciones']:
        st.dataframe(pd.DataFrame(st.session_state.s4['asignaciones']), use_container_width=True)

    st.divider()
    st.subheader("4. Comunicaciones y Enlace (C2)")
    malla_vhf = st.slider("Operatividad Malla VHF (Corta/Media Distancia) %", 0, 100, 100)
    malla_hf = st.slider("Operatividad Malla HF (Larga Distancia) %", 0, 100, 80)
    
    c_nodo, c_cripto = st.columns(2)
    with c_nodo: retransmision = st.checkbox("Nodos de Retransmisión Desplegados", value=True)
    with c_cripto: cripto = st.checkbox("Claves Criptográficas Sincronizadas", value=True)
    
    eficiencia_base = (malla_vhf * 0.7 + malla_hf * 0.3) / 100
    if not retransmision: eficiencia_base *= 0.8
    if not cripto: eficiencia_base *= 0.6
    
    st.session_state.s4['eficiencia_c2'] = eficiencia_base
    
    if eficiencia_base >= 0.8:
        st.success(f"✅ Enlace Óptimo. Multiplicador C2: x{eficiencia_base:.2f}")
    elif eficiencia_base >= 0.5:
        st.warning(f"⚠️ Enlace Degradado. Multiplicador C2: x{eficiencia_base:.2f}")
    else:
        st.error(f"❌ Pérdida de Comando y Control. Multiplicador C2: x{eficiencia_base:.2f}")

    st.divider()
    st.subheader("5. Movilidad y Vehículos")
    st.session_state.s4['vehiculos_servicio'] = st.slider("Vehículos Tácticos en Servicio %", 0, 100, st.session_state.s4.get('vehiculos_servicio', 100))

# ----------------- PANEL CONFRONTACIÓN -----------------
elif rol == "Confrontación (Monte Carlo)":
    st.header("Matriz de Confrontación Estocástica (Juego de Guerra)")
    
    if 'log_confrontacion' not in st.session_state: st.session_state.log_confrontacion = []
    vrc_base_propio = sum(item['VRC'] for item in st.session_state.s3.get('fuerzas_propias', [])) + st.session_state.s3.get('vrc_fuegos', 0)
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.s2.get('fuerzas_eno', []))
    
    with st.form("form_incidente"):
        fase_incidente = st.text_input("Incidente Táctico")
        col_s3, col_s2 = st.columns(2)
        with col_s3:
            deg_s3_min = st.number_input("Degradación Propia Mín (%)", min_value=0, max_value=100, value=10)
            deg_s3_max = st.number_input("Degradación Propia Máx (%)", min_value=0, max_value=100, value=25)
        with col_s2:
            deg_s2_min = st.number_input("Degradación Eno Mín (%)", min_value=0, max_value=100, value=5)
            deg_s2_max = st.number_input("Degradación Eno Máx (%)", min_value=0, max_value=100, value=15)
            
        if st.form_submit_button("Ejecutar Simulación Monte Carlo (1000 iteraciones)"):
            sim_s3 = np.random.uniform(deg_s3_min, deg_s3_max, 1000) / 100
            sim_s2 = np.random.uniform(deg_s2_min, deg_s2_max, 1000) / 100
            
            pcr_req = st.session_state.s3.get('pcr_requerido', 1.0)
            vrc_prop_sim = vrc_base_propio * (1 - sim_s3)
            vrc_eno_sim = vrc_base_eno * (1 - sim_s2)
            pcr_sim = np.divide(vrc_prop_sim, vrc_eno_sim, out=np.zeros_like(vrc_prop_sim), where=vrc_eno_sim!=0)
            
            prob_exito = np.mean(pcr_sim >= pcr_req) * 100
            st.session_state.log_confrontacion.append({
                "Incidente": fase_incidente, 
                "Probabilidad Éxito (%)": prob_exito
            })
            st.rerun()

    if st.session_state.log_confrontacion:
        st.dataframe(pd.DataFrame(st.session_state.log_confrontacion), use_container_width=True)

# ----------------- PANEL JEFE PLANA MAYOR -----------------
elif rol == "Jefe de la Plana Mayor":
    st.header("Sincronización Espacio-Tiempo (Gantt)")
    
    if 'cronograma' not in st.session_state:
        st.session_state.cronograma = pd.DataFrame(
            columns=["Actividad", "Responsable", "Inicio", "Fin", "Completado"],
            data=[
                ["Análisis de la misión", "J Pl My", "2026-10-01 08:00", "2026-10-01 10:00", False],
                ["Apreciación Inteligencia", "S2", "2026-10-01 10:00", "2026-10-01 12:00", False],
                ["Plan de Apoyo de Fuego", "S3", "2026-10-01 12:00", "2026-10-01 14:00", False],
                ["Apreciación Logística", "S4", "2026-10-01 14:00", "2026-10-01 16:00", False],
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
            
            gantt = alt.Chart(df_valido).mark_bar().encode(
                x=alt.X('Inicio:T', title='Horario'),
                x2='Fin:T',
                y=alt.Y('Actividad:N', sort='x', title='PPC'),
                color=alt.Color('Responsable:N'),
                tooltip=['Actividad', 'Responsable', 'Inicio', 'Fin']
            ).properties(height=350, title="Línea de Tiempo Operativa").interactive()
            
            st.altair_chart(gantt, use_container_width=True)
        except Exception:
            st.warning("Formato de fecha inválido. Utilice 'YYYY-MM-DD HH:MM'.")

# ----------------- PANEL COMANDANTE -----------------
elif rol == "Comandante (Resolución y Reserva)":
    st.header("Tablero de Resolución Táctica y Empeñamiento de Reserva")
    
    vrc_maniobra = sum(item['VRC'] for item in st.session_state.s3.get('fuerzas_propias', []))
    vrc_fuegos = st.session_state.s3.get('vrc_fuegos', 0)
    vrc_base_eno = sum(item['VRC'] for item in st.session_state.s2.get('fuerzas_eno', []))
    
    # Gestión de Reserva
    vrc_reserva_activa = 0
    if st.session_state.s3.get('reserva'):
        res = st.session_state.s3['reserva'][0]
        if res['Empeñada']:
            vrc_reserva_activa = res['VRC']
            st.info(f"⚡ RESERVA EMPEÑADA: '{res['Elemento']}' suma +{res['VRC']} VRC al dispositivo principal.")
        else:
            st.warning(f"🛡️ Reserva en posición ({res['Elemento']}): {res['VRC']} VRC listos para empeñar.")
            if st.button(f"⚡ ORDENAR EMPEÑAMIENTO DE RESERVA: {res['Elemento']}"):
                st.session_state.s3['reserva'][0]['Empeñada'] = True
                st.rerun()

    mod_moral = st.session_state.s1.get('moral', 1.0)
    mod_terreno = st.session_state.s2.get('terreno', 1.0)
    mod_logistico = st.session_state.s4.get('vehiculos_servicio', 100) / 100.0
    mod_c2 = st.session_state.s4.get('eficiencia_c2', 1.0)
    
    # Poder propio incluyendo la reserva si fue empeñada
    poder_propio = (((vrc_maniobra + vrc_reserva_activa) * mod_moral * mod_logistico) + vrc_fuegos) * mod_terreno * mod_c2
    poder_eno = vrc_base_eno * mod_terreno
    
    pcr_real = poder_propio / poder_eno if poder_eno > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Poder de Combate Propio", f"{poder_propio:.2f}")
    c2.metric("Poder de Combate Enemigo", f"{poder_eno:.2f}")
    c3.metric("PCR RESULTANTE", f"{pcr_real:.2f} : 1")
    
    exigencia_pcr = st.session_state.s3.get('pcr_requerido', 1.0)
    
    if pcr_real >= exigencia_pcr:
        st.success(f"✅ FACTIBLE: El PCR actual ({pcr_real:.2f}) supera la exigencia para la operación (Requiere {exigencia_pcr}).")
    else:
        st.error(f"⚠️ RIESGO INACEPTABLE: El PCR de {pcr_real:.2f} es inferior al umbral de {exigencia_pcr}.")

    st.divider()
    st.subheader("Matriz de Riesgo Operativo Ponderado")
    
    # Cálculo automático de niveles de riesgo
    riesgo_log = 3 if mod_logistico < 0.6 else (2 if mod_logistico < 0.8 else 1)
    riesgo_c2 = 3 if mod_c2 < 0.6 else (2 if mod_c2 < 0.8 else 1)
    riesgo_tactico = 3 if pcr_real < exigencia_pcr else (2 if pcr_real < exigencia_pcr * 1.2 else 1)
    
    score_riesgo = riesgo_log + riesgo_c2 + riesgo_tactico
    
    rc_col1, rc_col2 = st.columns(2)
    with rc_col1:
        st.markdown(f"- **Riesgo Táctico (Brecha PCR):** {'🔴 Alto' if riesgo_tactico==3 else ('🟡 Moderado' if riesgo_tactico==2 else '🟢 Bajo')}")
        st.markdown(f"- **Riesgo Logístico (Vehículos S4):** {'🔴 Alto' if riesgo_log==3 else ('🟡 Moderado' if riesgo_log==2 else '🟢 Bajo')}")
        st.markdown(f"- **Riesgo C2 (Comunicaciones):** {'🔴 Alto' if riesgo_c2==3 else ('🟡 Moderado' if riesgo_c2==2 else '🟢 Bajo')}")
        
    with rc_col2:
        if score_riesgo >= 7:
            st.error("🔴 CLASIFICACIÓN GLOBAL: RIESGO INACEPTABLE (Requiere revisión completa del Plan o empeñamiento de Reserva).")
        elif score_riesgo >= 5:
            st.warning("🟡 CLASIFICACIÓN GLOBAL: RIESGO MODERADO / ALTO (Autorizado bajo supervisión estricta de la Plana Mayor).")
        else:
            st.success("🟢 CLASIFICACIÓN GLOBAL: RIESGO BAJO (Operación óptima y balanceada).")

# ----------------- PANEL GESTIÓN -----------------
elif rol == "Gestión de Datos":
    st.header("Gestión del Monitor")
    if st.button("⚠️ Limpiar Tablero de Comando", type="primary"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
