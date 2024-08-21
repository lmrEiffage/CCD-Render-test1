#Lucas Martínez Rodríguez - Eiffage

#IMPORTANTE: 
#DAR PERMISOS AL DIRECTORIO DE LECTURA, ESCRITURA Y EJECUCIÓN !!!
#CUIDADO AL PARSEAR CON LOS ESPACIOS DE NOMBRE DEL ARCHIVO ¡¡¡
#CUIDADO CON LOS ARCHIVOS QUE SE PARSEAN (XML.etree no tiene ningún tipo de forma de detectar intenciones maliciosas dentre de un kml)
#Al INICIAR EL PROGRAMA TO DO LO QUE NO SEA UNA CARPETA DEL MISMO SE BORRA DEL DIRECTORIO¡¡¡

import  os, time
import streamlit as st
from streamlit_option_menu import option_menu
import hydralit_components as hc
import pandas as pd

def set_streamlit_page_config_once():
    try:
        st.set_page_config(
            layout="centered",
            page_title="CCD-Eiffage/home",
            page_icon=":small_airplane:",
        )
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in str(e):
            return
        raise e

def menu():
    over_theme = {
        'menu_background': ' #d5d5d5 ', 
        'menu_font_size': '24px',
        'border_width': '2px',        
        'icon_size': '24px '
    }    
    
    menu_data = [
    {'label':"HOME 🏛️"},
    {'label':"EIFFAGE"}
    ]

    menu_id = hc.nav_bar(menu_definition=menu_data,
                          override_theme=over_theme,
                        key='h') 
    return menu_id

@st.dialog("Describe tu problema/sugerencia")
def reporte(item):
    reason = st.text_input(item)
    if st.button("Submit"):
        st.session_state.vote = {"item": item, "reason": reason}
        
def home():
    st.markdown("""
        <div style="text-align: center;">
            <h4>BIENVENIDO</h4>
        </div>
        """, unsafe_allow_html=True) 
    st.write(" ")
    st.write("Esta aplicacilón está diseñada con el fin de proporcionar una plataforma intuitiva y eficaz para crear, monitorear y gestionar rutas de drones ------------------------------------------------------------------- ACTUALMENTE EN DESARROLLO: VERSIÓN 0.5")
    st.write(" ")
    st.write(" ")
    
    with st.expander("USO 🖥️"):     
        c1, c2, c3 = st.columns(3)
        st.write("En todas las páginas se propociona una pestaña ""INFO"" donde se profundiza más sobre las características específicas de cada faceta de la aplicación")
        with c1: 
            st.subheader("CREAR RUTAS")
            
        with c2: 
            st.subheader("MONITOREO Y ESTADÍSTICAS")
            
        with c3: 
            st.subheader("INICIO DE SESIÓN Y AJUSTES")

    with st.expander("SOPORTE 📢"):
        st.write(" ")
        st.write("Ayúdame a Mejorar")
        st.write(" ")
        if st.button("BUG"):
            reporte("BUG")
            
        if st.button("POSIBLE MEJORA"):
            reporte("BUG")
                
    with st.expander("FUTURAS MEJORAS 🔜"):
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.write("test")
            
        with c2: 
            st.write("test")
            
        with c3: 
            st.write("test")
            
    with st.expander("CONTACTO 📞"):
        st.write("test")
    
    with st.expander("DEPENDENCIAS ❗"):
        st.write("")
        
def usage():
    st.info("DEVELOPING")
    
def eiffage(): 
    st.info("DEVELOPING")

def main():
    selected = menu()
    if selected == "HOME 🏛️":
        home()
    if selected ==  "EIFFAGE":
        eiffage()

        
main()
