import streamlit as st
from motor_ia import consultar_agente

st.set_page_config(page_title="Agente Irapuato", page_icon="🍓")

# Inyección de CSS para el Botón Flotante Circular
st.markdown("""
    <style>
    /* Forzamos un botón circular más grande en la esquina inferior derecha */
    button[kind="primary"] {
        position: fixed !important;
        bottom: 90px !important; 
        right: 30px !important;
        width: 75px !important;       /* Aumentamos el ancho */
        height: 75px !important;      /* Aumentamos el alto */
        z-index: 9999 !important;
        border-radius: 50% !important; 
        box-shadow: 0px 6px 14px rgba(0,0,0,0.4) !important;
        background-color: #c2185b !important; 
        color: white !important;
        border: none !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    button[kind="primary"]:hover {
        background-color: #a0134b !important;
        transform: scale(1.05); /* Pequeño efecto al pasar el mouse */
        transition: 0.2s;
    }
    /* Agrandamos el ícono internamente */
    button[kind="primary"] div, button[kind="primary"] p {
        font-size: 35px !important; 
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍓 Agente Virtual - Municipio de Irapuato 🍓")
st.write("Hola, soy tu asistente personal del municpio. ¿En qué te puedo orientar hoy?")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Botón flotante sin tooltip
if st.button("🔄", type="primary"):
    st.session_state.mensajes = []
    st.rerun()

# Botones de sugerencias rápidas
st.write("💡 **Consultas frecuentes:**")
col1, col2 = st.columns(2)
pregunta_rapida = None

if col1.button("🏢 Quiero abrir un negocio", use_container_width=True):
    pregunta_rapida = "Quiero abrir un nuevo negocio, ¿qué necesito?"
    
if col2.button("🏗️ Voy a realizr una construcción", use_container_width=True):
    pregunta_rapida = "Quiero hacer una nueva construcción, ¿qué trámites ocupo?"

st.divider()

# Renderizado de la memoria del chat
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

# Caja de texto inferior nativa
pregunta_usuario = st.chat_input("Escribe tu duda sobre algún trámite aquí...")

# Evaluación de la entrada (atajo o texto libre)
pregunta_final = pregunta_usuario or pregunta_rapida

if pregunta_final:
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta_final})
    with st.chat_message("user"):
        st.markdown(pregunta_final)

    with st.chat_message("assistant"):
        with st.spinner("Consultando las normativas oficiales de Irapuato..."):
            
            ultimos_mensajes = st.session_state.mensajes[-5:-1]
            historial = "\n".join([f"{m['rol']}: {m['contenido']}" for m in ultimos_mensajes])
            
            respuesta = consultar_agente(pregunta_final, historial)
            st.markdown(respuesta)
            
    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})