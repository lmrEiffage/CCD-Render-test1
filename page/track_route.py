#Lucas Martínez Rodríguez - Eiffage

#IMPORTANTE: 
#DAR PERMISOS AL DIRECTORIO DE LECTURA, ESCRITURA Y EJECUCIÓN !!!
#CUIDADO AL PARSEAR CON LOS ESPACIOS DE NOMBRE DEL ARCHIVO ¡¡¡
#CUIDADO CON LOS ARCHIVOS QUE SE PARSEAN (XML.etree no tiene ningún tipo de forma de detectar intenciones maliciosas dentre de un kml)
#Al INICIAR EL PROGRAMA TO DO LO QUE NO SEA UNA CARPETA DEL MISMO SE BORRA DEL DIRECTORIO¡¡¡

import folium.map
import folium, os, time, shutil, simplekml
import pandas as pd
import xml.etree.ElementTree as ET
from streamlit_folium import st_folium
from streamlit_folium import folium_static, st_folium
from openpyxl import Workbook
from openpyxl import load_workbook
from datetime import datetime
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import AgGrid, GridUpdateMode,ColumnsAutoSizeMode, GridOptionsBuilder, JsCode
import streamlit as st
from folium.plugins import Fullscreen
import streamlit.components.v1 as components
import hydralit_components as hc
import dash_ag_grid as dag
from dash import Dash, html, Input, Output, ClientsideFunction, State, clientside_callback, callback
import uuid

#Directorio del workspace 
dirname = os.path.dirname(__file__)

#Out of pages
parent_dir = os.path.dirname(dirname)

path_markers = os.path.join(parent_dir, "data", "markers.csv")
routes_path = os.path.join(parent_dir, "Trayectorias")
path_dron = os.path.join(parent_dir, "data", "dron.csv")
path = os.path.join(parent_dir, "data", "rutas.csv")

def generate_unique_key():
    return f"folium_map_{uuid.uuid4().hex}"

@st.cache_data
def searching_trajectories():
    progress_bar = st.progress(0)
    with st.spinner('Loading...'):
        time.sleep(1.75)
    progress_bar.progress(100)
    progress_bar.empty()

def listar_carpetas():
    try:
        elementos = os.listdir(routes_path)
        carpetas = [carpeta for carpeta in elementos if os.path.isdir(os.path.join(routes_path, carpeta))]
        df_carpetas = pd.DataFrame(carpetas, columns=['Carpeta'])
        return df_carpetas
            
    except FileNotFoundError:
        st.error("El directorio especificado no existe.")
        return []
    except PermissionError:
        st.error("No tienes permiso para acceder a este directorio.")
        return []
    except Exception as e:
        st.error(f"Se produjo un error: {e}")
        return []
    
def prepare_rutas():
    try:
        if not os.path.exists(path):
            df_vacio = pd.DataFrame()
            df_vacio.to_csv(path, index=False)
            return []
            
        else:
            rutas = listar_carpetas()
            rutas.to_csv(path, index=False)
            return rutas            

    except Exception as e: 
        st.error('ERROR creating/reading rutas.csv')
        
def prepare_data():
    if 'mapa' not in st.session_state:
       st.session_state.map_config = {"center": [40.4637, 3.7492], "zoom": 5.5}

    if 'dron' not in st.session_state:
        st.session_state['dron'] = []
        
    if 'markers' not in st.session_state:
        st.session_state['markers'] = []
        
    if 'excell' not in st.session_state:
        st.session_state['excell'] = []
    
    if 'mapa' not in st.session_state:
        st.session_state['mapa'] = []
        
    if 'waypoints' not in st.session_state:
        st.session_state['waypoints'] = []
        
    if 'name' not in st.session_state:
        st.session_state['name'] = []
        
    if 'time' not in st.session_state:
        st.session_state['time'] = 0
        
    if "start" not in st.session_state: 
        st.session_state["start"] = False
        
    if "paused" not in st.session_state:
        st.session_state["paused"] = 0
        
    if "markers_achieved" not in st.session_state:
        st.session_state["markers_achieved"] = 0
        
    searching_trajectories()
    try:
        if not os.path.exists(path_dron):
            df_vacio = pd.DataFrame(columns=['longitude', 'latitude', 'altitud'])
            df_vacio.to_csv(path_dron, index=False)
            if not os.path.exits(path_markers):
                df_vacio_m = pd.DataFrame(columns=['longitude', 'latitude', 'altitud'])
                df_vacio_m.to_csv(path_dron, index=False)

            return                    

    except Exception as e: 
        st.error('ERROR: creating/reading rutas.csv')

def compare_last_two_rows(df):
    if len(df) < 2:
        return False  # No hay suficientes filas para comparar

    latitudes_equal = df.iloc[0]['latitude'] == df.iloc[1]['latitude']
    longitudes_equal = df.iloc[0]['longitude'] == df.iloc[1]['longitude']
    alturas_equal = df.iloc[0]['altitud'] == df.iloc[1]['altitud']
    
    return latitudes_equal and longitudes_equal and alturas_equal

@st.cache_data
def read_data(select_ruta):
    try:
        path = os.path.join(routes_path, select_ruta)
        excell = load_workbook(path + "/" + select_ruta + ".xlsx")
        waypoints = pd.read_csv(path + "/waypoints.csv")
        #landmarks = pd.read_csv(path + "/landmarks.csv")
        with open(path + "/"+select_ruta + ".html", 'r', encoding='utf-8') as f:
            html_map = f.read()
        
        data = [excell, waypoints, html_map]
        return data
            
    except:
        st.sidebar.error("Error: missing files")
        return        

def extract_markers(waypoints):
    
    df = pd.read_csv(waypoints)
    primero = df.iloc[0]
    ultimo = df.iloc[-1]
    penultimo = df.iloc[-2]
    
    return primero, ultimo, penultimo

def create_marker(marker):
    return folium.Marker(location=[marker["latitude"], marker["longitude"]])
    
def dron_marker():
    marker = extract_markers(path_dron)

    if marker[1]["latitude"] !=  marker[2]["latitude"] or marker[1]["longitude"] !=  marker[2]["longitude"]:
        st.session_state["paused"] = 0
        st.session_state["dron"].append((marker[1]["latitude"], marker[1]["longitude"]))
        st.session_state["markers"].append(create_marker(marker[1]))
    elif  marker[1]["latitude"] ==  marker[2]["latitude"] and marker[1]["longitude"] ==  marker[2]["longitude"]:
        st.session_state["paused"] = 1

@st.cache_data
def base_map():
    m = folium.Map(location=[40,3], tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',         attr='Imagery © Esri, Maxar, Earthstar Geographics, and the GIS User Community', zoom_start = 5)
    fg = folium.FeatureGroup(name="Markers")

    return m, fg

@st.fragment(run_every=0.5)
def draw_map():
    m, fg = base_map()
    
    #for marker in st.session_state["markers"]:
        #fg.add_child(marker)
    if st.session_state["markers"]: 
        fg.add_child(st.session_state["markers"][-1])
        
    st_folium(
    m,
    feature_group_to_add=fg,
    key="user-map",
    returned_objects=[],
    use_container_width=True,
    )
    
    if st.session_state["dron"] and st.session_state["start"] == True:
        st.write("Tracking ✅")
        st.write("DRONE POSITION (", "LAT: ",st.session_state["dron"][-1][0],"LON: ", st.session_state["dron"][-1][1], ")")
        if st.session_state["paused"]  == 1:
            st.info("DRONE AT REST")
        if st.session_state["paused"]  == 2:
            st.error("SIGNAL LOST")
    else:
        st.write("Tracking ❌")

def menu():
    over_theme = {
        'menu_background': ' #d5d5d5 ', 
        'menu_font_size': '24px',         
        'border_width': '2px',        
        'icon_size': '24px '
    }    
    
    menu_data = [
    {'label':"TRACK 🚀"},
    {'label':"INFO  ℹ️"},
    ]

    menu_id = hc.nav_bar(menu_definition=menu_data,
                          override_theme=over_theme,
                        key="menu4") 
    return menu_id

def prepare_data_routes():
    try:
        if not os.path.exists(path):
            df_vacio = pd.DataFrame()
            df_vacio.to_csv(path, index=False)
            return []
            
        else:
            rutas = listar_carpetas()
            rutas.to_csv(path, index=False)
            return rutas            

    except Exception as e: 
        st.error('ERROR creating/reading rutas.csv')
    
def ready(rutas):
    if not rutas.empty:  
        select_ruta = st.sidebar.selectbox('Trajectories', rutas, key="test")
        if select_ruta:
            data = read_data(select_ruta)
            st.session_state["waypoints"] = data[1]
            st.session_state["excell"] = data[0]
            st.session_state["mapa"] = data[2]
            st.session_state["name"] = select_ruta
            
            return True
        
    else: 
        st.sidebar.info("NOT TRAJECTORIES AVAILABLE YET")
        return False

def info_dron():
    st.write("DRONE POSITION: ")
    st.write("LAT", st.session_state["dron"][-1][0])
    st.write("LON", st.session_state["dron"][-1][1])
    
def display(): 
    c1, c2, c3, c4, c5 = st.columns([0.30, 0.02, 0.50, 0.02, 0.16])
    st.session_state["col_info"] = c5
    st.sidebar.write(" ")
    start = st.sidebar.toggle("START TRACKING 🛩️")

    with c1: 
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>PLANED TRAJECTORY {st.session_state["name"]}</h4>
        </div>
        """, unsafe_allow_html=True)  
        mapa = st.components.v1.html(st.session_state["mapa"], height=500)

        with st.expander("waypoints"):
            st.write(st.session_state["waypoints"])
                
    with c3:
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>TRACKING {st.session_state["name"]}</h4>
        </div>
        """, unsafe_allow_html=True)  
        if start:
            st.session_state["start"] = True
            st.fragment(dron_marker, run_every=1.0)()
            
        else:
            st.session_state["start"] = False

        draw_map()
        
    with c5: 
        st.markdown("""
        <div style="text-align: center;">
            <h4>INFO</h4>
        </div>
        """, unsafe_allow_html=True)
                    
        st.write("---")
        st.button("SAVE DATA")
        st.write("---")
        st.markdown("""
        <div style="text-align: center;">
            <span style="font-size: 18px;">DATA</span>
        </div>
        """, unsafe_allow_html=True)
        st.write(" ")
        st.write("COMPLETED TRAJECTORY: ")
        st.write(" ")
        st.write("WAYPOINTS ACHIEVED: ")
        st.write(" ")
        st.write("TOF: ")
        st.write(" ")
        st.write("BATTERY: ")
    
def info():
    st.info("DEVELOPING ")
    
def main():
    prepare_data()
    selected = menu()
    rutas = prepare_data_routes()
    ok = ready(rutas)

    if ok == True:
        if selected == "TRACK 🚀":
            display()           
        if selected == "INFO  ℹ️":
            info()
    else:
        st.sidebar.info("NOT TRAJECTORIES AVAILABLE YET")

    
main()