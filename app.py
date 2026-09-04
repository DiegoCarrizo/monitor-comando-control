import streamlit as st
import pandas as pd
from fpdf import FPDF

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
rol = st.sidebar.radio("Seleccione Panel:", ["G1 - Personal", "G2 - Inteligencia", "G3 - Operaciones", "G4 - Materiales", "Comandante", "Gestión de Datos"])

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
    st.header("G2: Ambiente Geográfico y Orden de Batalla Enemigo")
    st.markdown("Evaluación matemática de capacidades enemigas y terreno operacional (Ref. ROD-71-01-II, Anexo 7)[cite: 1]")
    
    # 1. Ambiente Geográfico y Terreno
    st.subheader("1. Entorno y Terreno a Operar")
    ambientes = ["Insular", "Desértico", "Desértico Patagónico", "Montaña", "Monte", "Llanura", "Urbano"]
    st.session_state.g2['ambiente'] = st.selectbox("Ambiente Geográfico Principal", ambientes)
    
    terreno_eno = st.selectbox("Aptitud del Terreno para el Enemigo", ["Favorable", "Limitado", "Desfavorable"])
    # Asignación de ponderación al PCR del enemigo
    mod_terreno = {"Favorable": 1.2, "Limitado": 0.8, "Desfavorable": 0.5}
    st.session_state.g2['terreno'] = mod_terreno[terreno_eno]
    
    st.info(f"Modificador de terreno enemigo fijado en: x{st.session_state.g2['terreno']} (Este valor alterará el PCR en el panel del Comandante).")
    
    st.divider()
    
    # 2. Carga Parametrizada de Fuerzas Enemigas
    st.subheader("2. Ponderación Analítica de Elementos Enemigos")
    
    with st.form("form_eno_avanzado"):
        tipo_eno = st.text_input("Denominación del Elemento (Ej: Batallón de Infantería Enemigo)")
        
        col_fza, col_alc = st.columns(2)
        with col_fza:
            efectivos_pie = st.number_input("Número Relativo de Fuerzas a Pie", min_value=0, value=100)
            autonomia = st.number_input("Autonomía Operativa (Km/Días de alcance logístico)", min_value=0.0, value=50.0, step=10.0)
        with col_alc:
            alcance_armas = st.number_input("Alcance Promedio Armas de Dotación (Km)", min_value=0.0, value=2.0, step=0.1)
            
        st.markdown("**Capacidades Tecnológicas Agregadas (Multiplicadores de Fuerza)**")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            has_drones = st.checkbox("Sistemas Drones / UAS")
        with col_t2:
            has_nocturna = st.checkbox("Capacidad Nocturna Estándar")
        with col_t3:
            has_termografica = st.checkbox("Visión Termográfica Avanzada")
            
        submit_eno = st.form_submit_button("Calcular VRC y Cargar al Tablero")
        
        if submit_eno and tipo_eno:
            # A. Ecuación base de combate (Masa + Fuego + Proyección)
            vrc_base = (efectivos_pie * 0.01) + (alcance_armas * 0.15) + (autonomia * 0.005)
            
            # B. Ponderaciones tecnológicas
            mod_drones = 1.25 if has_drones else 1.0
            # Si tiene termográfica, anula la nocturna estándar por superioridad[cite: 1]
            mod_optica = 1.35 if has_termografica else (1.15 if has_nocturna else 1.0)
            
            vrc_calculado = vrc_base * mod_drones * mod_optica
            
            # Se guarda con la clave 'VRC' para mantener compatibilidad con la suma del Panel Comandante
            st.session_state.g2['fuerzas_eno'].append({
                'Elemento': tipo_eno,
                'VRC': round(vrc_calculado, 2),
                'Base': round(vrc_base, 2),
                'Armas(Km)': alcance_armas,
                'Fza Pie': efectivos_pie
            })
            
    if st.session_state.g2['fuerzas_eno']:
        st.dataframe(pd.DataFrame(st.session_state.g2['fuerzas_eno']), use_container_width=True)
        vrc_bruto_eno = sum(item['VRC'] for item in st.session_state.g2['fuerzas_eno'])
        
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("VRC Bruto Enemigo (Sin Terreno)", f"{vrc_bruto_eno:.2f}")
        c_res2.metric("VRC Enemigo Proyectado (Con Terreno)", f"{(vrc_bruto_eno * st.session_state.g2['terreno']):.2f}")

# ----------------- PANEL G3 -----------------
elif rol == "G3 - Operaciones":
    st.header("G3: Maniobra, Exploración y Poder de Combate Propio")
    st.markdown("Diseño de la operación y cálculo de PCR integrando multiplicadores de G1[cite: 1]")
    
    # 1. Selección Dinámica del Tipo de Operación
    tipo_op_principal = st.selectbox("Clasificación de la Operación", ["Ofensiva", "Defensiva", "Complementaria"])
    
    if tipo_op_principal == "Ofensiva":
        op_detallada = st.selectbox("Tipo de Operación Ofensiva", ["Ataque Ruptura (5:1)", "Ataque Frontal (3:1)", "Ataque Envolvente", "Explotación"])
    elif tipo_op_principal == "Defensiva":
        op_detallada = st.selectbox("Tipo de Operación Defensiva", ["Defensa de Zona (0.33:1)", "Defensa Móvil", "Acción Retardante"])
    else:
        op_detallada = st.selectbox("Tipo de Operación Complementaria", ["Exploración", "Seguridad", "Marcha de Aproximación", "Infiltración"])
        
    st.session_state.g3['tipo_operacion'] = op_detallada.split(" ")[0]
    
    # Asignación de PCR Requerido doctrinario (si aplica)
    if "(" in op_detallada:
        st.session_state.g3['pcr_requerido'] = float(op_detallada.split("(")[1].split(":")[0])
    else:
        st.session_state.g3['pcr_requerido'] = 1.0 # Valor nominal para operaciones sin PCR estricto
        
    st.divider()
    st.subheader(f"Diseño del Elemento para: {st.session_state.g3['tipo_operacion']}")
    
    # 2. Formulario Dinámico de Carga de Medios y Personal
    with st.form("form_op_propia"):
        elemento_nombre = st.text_input("Unidad / Fracción a emplear", placeholder="Ej: Escuadrón de Exploración de Caballería Blindado 11")
        
        col_amb, col_luz = st.columns(2)
        with col_amb:
            ambiente = st.selectbox("Ambiente Geográfico de la Operación", ["Insular", "Desértico", "Desértico Patagónico", "Montaña", "Monte", "Llanura", "Urbano"], index=5)
        with col_luz:
            condicion_luz = st.selectbox("Condición de Iluminación", ["Diurna", "Nocturna"])
            
        st.markdown("**Personal y Material de Dotación**")
        col_p, col_a, col_v = st.columns(3)
        with col_p:
            efectivos = st.number_input("Cantidad de Personal Empleado", min_value=1, value=50)
        with col_a:
            alcance = st.number_input("Alcance Promedio Armamento (Km)", min_value=0.0, value=2.5, step=0.1)
        with col_v:
            autonomia = st.number_input("Autonomía de Vehículos (Km)", min_value=0.0, value=300.0, step=10.0)
            
        st.markdown("**Capacidades Tecnológicas Propias**")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            vn_estandar = st.checkbox("Sistemas de Visión Nocturna Estándar")
        with col_v2:
            vn_termo = st.checkbox("Sistemas de Visión Termográfica")
            
        st.markdown("**Desarrollo y Tiempos**")
        tiempo_est = st.number_input("Tiempo Estimado de Ejecución (Horas)", min_value=1, value=12)
        fases_op = st.text_area("Fases de la Operación (Manual)", placeholder="Ej: 1. Infiltración. 2. Ocupación PO. 3. Vigilancia. 4. Exfiltración.")
        
        submit_g3 = st.form_submit_button("Calcular PCR del Elemento y Asignar")
        
        if submit_g3 and elemento_nombre:
            # A. Ecuación base (Equivalente al cálculo G2 para estandarización)
            vrc_base = (efectivos * 0.01) + (alcance * 0.15) + (autonomia * 0.005)
            
            # B. Ponderación por visibilidad y tecnología (ROD-71-01-II, Tabla de Oportunidad)[cite: 1]
            mod_optica = 1.0
            if condicion_luz == "Nocturna":
                if vn_termo:
                    mod_optica = 1.5 # Superioridad tecnológica
                elif vn_estandar:
                    mod_optica = 1.0 # Compensa la penalidad nocturna
                else:
                    mod_optica = 0.5 # Severa penalidad sin instrumentos
            
            # C. Integración de la Moral (Desde G1)
            moral_actual = st.session_state.g1.get('moral', 1.0)
            
            # Cálculo final del VRC de la fracción
            vrc_final = vrc_base * mod_optica * moral_actual
            
            st.session_state.g3['fuerzas_propias'].append({
                'Elemento': elemento_nombre,
                'VRC': round(vrc_final, 2),
                'Base': round(vrc_base, 2),
                'Luz': condicion_luz,
                'Moral G1': moral_actual,
                'Fases': fases_op
            })
            
    # 3. Visualización de Resultados
    if st.session_state.g3['fuerzas_propias']:
        st.dataframe(pd.DataFrame(st.session_state.g3['fuerzas_propias']), use_container_width=True)
        vrc_bruto_propio = sum(item['VRC'] for item in st.session_state.g3['fuerzas_propias'])
        
        c_r1, c_r2 = st.columns(2)
        c_r1.metric("VRC Total Propio (Integrado con Moral y Óptica)", f"{vrc_bruto_propio:.2f}")
        c_r2.metric("PCR Doctrinario Requerido", f"{st.session_state.g3['pcr_requerido']}:1")

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
        # ----------------- PANEL GESTIÓN DE DATOS -----------------
elif rol == "Gestión de Datos":
    st.header("Gestión del Monitor y Exportación")
    st.markdown("Generación de Anexos y limpieza de la matriz de estado.")
    
    st.markdown("**Exportar Apreciación de Situación (PDF)**")
    if st.button("Generar Reporte PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Monitor de Comando y Control - Resumen", ln=True, align='C')
        pdf.ln(5)
        
        # Extraer datos de memoria
        g1 = st.session_state.get('g1', {})
        g2 = st.session_state.get('g2', {})
        g3 = st.session_state.get('g3', {})
        g4 = st.session_state.get('g4', {})
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="G1 - Personal", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Moral (Calculada): {g1.get('moral', 'N/A')} | Exp: {g1.get('experiencia', 'N/A')}", ln=True)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="G2 - Inteligencia", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Ambiente: {g2.get('ambiente', 'N/A')} | Terreno: {g2.get('terreno', 'N/A')}", ln=True)
        for eno in g2.get('fuerzas_eno', []):
            pdf.cell(200, 10, txt=f"- {eno['Elemento']} (VRC: {eno['VRC']})", ln=True)
            
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="G3 - Operaciones", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Operación: {g3.get('tipo_operacion', 'N/A')} | PCR Requerido: {g3.get('pcr_requerido', 'N/A')}", ln=True)
        for prop in g3.get('fuerzas_propias', []):
            pdf.cell(200, 10, txt=f"- {prop['Elemento']} (VRC: {prop['VRC']})", ln=True)
            
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="G4 - Materiales", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Mun (Cl V): {g4.get('clase_v', 'N/A')}% | Comb (Cl III): {g4.get('clase_iii', 'N/A')}%", ln=True)
        
        # Procesar y descargar
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 Descargar Apreciación en PDF", data=pdf_bytes, file_name="apreciacion_situacion.pdf", mime="application/pdf")
        
    st.divider()
    st.markdown("**Reinicio del Sistema**")
    st.markdown("Elimina todas las unidades cargadas y restablece los parámetros a sus valores nominales.")
    if st.button("⚠️ Limpiar Tablero de Comando", type="primary"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
