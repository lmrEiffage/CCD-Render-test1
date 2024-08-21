#Lucas Martínez Rodríguez - Eiffage

#IMPORTANTE: 
#DAR PERMISOS AL DIRECTORIO DE LECTURA, ESCRITURA Y EJECUCIÓN !!!
#CUIDADO AL PARSEAR CON LOS ESPACIOS DE NOMBRE DEL ARCHIVO ¡¡¡

import streamlit as st

def set_streamlit_page_config_once():
    try:
        st.set_page_config(
            layout="wide",
            page_title="CCD-Eiffage",
            page_icon=":small_airplane:"
        )
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in str(e):
            return
        raise e

set_streamlit_page_config_once()

import toml, time, os
import shutil

dirname = os.path.dirname(__file__)

@st.cache_data
def prepare_data():
    items = os.listdir(dirname)
    exclude_file = ['app_alpha.py', 'landmarks.csv', 'requirements.txt', 'package.json', 'package-lock.json']
    exclude_dirs = ['.streamlit', 'data', 'Images', 'page', '__pycache__', 'Trayectorias', 'node_modules', 'build']
        
    for item in items:
        item_path = os.path.join(dirname, item)
        
        if os.path.isfile(item_path) and item not in exclude_file:
            os.remove(item_path)
        
        elif os.path.isdir(item_path) and item not in exclude_dirs:
            shutil.rmtree(item_path)    

prepare_data()

if "loading" not in st.session_state:
    st.session_state["loading"] = False

if st.session_state["loading"] == False:         
    st.session_state["loading"] = True
    container2 = st.empty()
        
    container2.markdown(f"""
    <div style="text-align: center;">
        <h3>CENTRO DE CONTROL DE DRONES 🛩️</h3>
    </div>
    """, unsafe_allow_html=True)

    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    # Actualizar la barra de progreso y el mensaje
    for percent_complete in range(100):
        # Calcular el porcentaje completado
        progress_percentage = percent_complete + 1

        # Actualizar el mensaje basado en el porcentaje
        if progress_percentage < 25:
            message = "Charging drones... 🔋" 
        elif progress_percentage < 50:
            message = "Downloading data... 📥" 
        elif progress_percentage < 90:
            message = "Processing data... 🌐"
        else:
            message = "Ready to go... ✈️" 

        # Mostrar el mensaje y actualizar la barra de progreso
        progress_text = f"{message} ({progress_percentage}%)"
        my_bar.progress(progress_percentage, text=progress_text)
        time.sleep(0.05)
    
    # Esperar un momento antes de limpiar
    time.sleep(1)
    
    container2.empty()
    my_bar.empty()

p1 = st.Page("page/home.py", title="home", icon=":material/home:")
p6 = st.Page("page/setting.py", icon=":material/settings:")
p7 = st.Page("page/login.py", icon=":material/login:")
p8 = st.Page("page/logout.py", icon=":material/logout:")

p2 = st.Page("page/create_route.py", icon=":material/public:", title='create')
p3 = st.Page("page/edit.py", icon=":material/edit:",title='edit')
p4 = st.Page("page/track_route.py", icon=":material/rocket_launch:", title='track')
p5 = st.Page("page/route_stats.py", icon=":material/query_stats:", title='stats')

pg = st.navigation([p7, p1, p2,p3,p4,p5, p6, p8])
pg.run()


