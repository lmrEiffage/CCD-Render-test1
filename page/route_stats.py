#Lucas Martínez Rodríguez - Eiffage

#IMPORTANTE: 
#DAR PERMISOS AL DIRECTORIO DE LECTURA, ESCRITURA Y EJECUCIÓN !!!
#CUIDADO AL PARSEAR CON LOS ESPACIOS DE NOMBRE DEL ARCHIVO ¡¡¡
#CUIDADO CON LOS ARCHIVOS QUE SE PARSEAN (XML.etree no tiene ningún tipo de forma de detectar intenciones maliciosas dentre de un kml)
#Al INICIAR EL PROGRAMA TO DO LO QUE NO SEA UNA CARPETA DEL MISMO SE BORRA DEL DIRECTORIO¡¡¡

import streamlit as st
import time, os
import pandas as pd
import streamlit.components.v1 as components
from openpyxl import load_workbook
import hydralit_components as hc
import exifread
import io
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, FastMarkerCluster
from PIL import Image 
import leafmap
import geopandas as gp
import streamlit.components.v1 as html
from IPython.display import HTML, display
import webbrowser

#Directorio del workspace 
dirname = os.path.dirname(__file__)

#Out of pages
parent_dir = os.path.dirname(dirname)

path_markers = os.path.join(parent_dir, "data", "markers.csv")
routes_path = os.path.join(parent_dir, "Trayectorias")
path_dron = os.path.join(parent_dir, "data", "dron.csv")
path = os.path.join(parent_dir, "data", "rutas.csv")
carpeta_rutas = os.path.join(parent_dir, "Revisar_ruta")

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
    
def prepare_data():
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

def display(rutas):
    col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
    st.sidebar.write("----")
    
    select_ruta = st.sidebar.selectbox('Trajectories', rutas)
    st.sidebar.write("----")
    show = st.sidebar.button("Show stats 👁️")
    if select_ruta:
        data = read_data(select_ruta)
            
        with col1: 
            st.subheader("Planed trajectory: "+select_ruta)
            st.components.v1.html(data[2], height=500)
            sheet = data[0].active
            modelo = sheet['H5'].value #H5
            piloto = sheet['E2'].value #E2
            ruta = sheet['C5'].value #C5
            tiempo = sheet['B9'].value #B9
            st.write("PILOT: ", piloto)
            st.write("DRONE: ", modelo)
            st.write("TRAJECTORY: ", ruta)
            st.write("TOF: ", tiempo)

            with st.expander("waypoints"):
                st.write(data[1])
                
        with col2:
            st.subheader("Completed trajectory")
            st.write("en desarrollo")

            
        if show:
            with col3: 
                st.subheader("Stats")
                st.write("en desarrollo")

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
        
    if 'markers_set_path' not in st.session_state:
        st.session_state['markers_set_path'] = []
        
    if "photos" not in st.session_state:
        st.session_state["photos"] = []
        
    if "path" not in st.session_state:
        st.session_state["path"] = "Empty"
        
    if "test2" not in st.session_state:
        st.session_state["test2"] = []
        
    if "bounds" not in st.session_state:
        st.session_state["bounds"] = []



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

def info(): 
    return 0

def menu():
    over_theme = {
        'menu_background': ' #d5d5d5 ', 
        'menu_font_size': '24px',         
        'border_width': '2px',        
        'icon_size': '24px '
    }    
    
    menu_data = [
    {'label':"STATS 📊"},
    {'label':"REVIEW FLIGHT PATH 🗺️"},
    {'label':"INFO  ℹ️"},
    ]

    menu_id = hc.nav_bar(menu_definition=menu_data,
                          override_theme=over_theme,
                        ) 
    return menu_id

def convert_to_decimal(grados, minutos, segundos, ref): 
    decimal = grados + (minutos / 60) + (segundos / 3600)
    ref_str = str(ref)
    
    if ref_str == "S" or ref_str == "W":
        decimal = -decimal

    return decimal

def create_marker(data, color = "blue"):
    return folium.Marker(location=[data["latitude"], data["longitude"]], popup=data["name"], tooltip=data["altitud"], icon=folium.Icon(color=color))

#@st.cache_data
def extract_exif_from_uploaded_file(uploaded_file):
    with io.BytesIO(uploaded_file.read()) as file:
        tags = exifread.process_file(file)
        gps_info = {}
        
        lat = tags.get('GPS GPSLatitude')
        lat_ref = tags.get('GPS GPSLatitudeRef', 'N')
        lon = tags.get('GPS GPSLongitude')
        lon_ref = tags.get('GPS GPSLongitudeRef', 'E')
        alt = tags.get('GPS GPSAltitude')
        
        if lat and lat_ref:
            latitud = convert_to_decimal(float(lat.values[0]), float(lat.values[1]), (float(lat.values[2].num) / float(lat.values[2].den)), lat_ref)
        else: 
            latitud = None
            
        if lon and lon_ref: 
            longitud = convert_to_decimal(float(lon.values[0]), float(lon.values[1]), (float(lon.values[2].num) / float(lon.values[2].den)), lon_ref)
        else: 
            longitud = None
            
        if alt: 
            altitud = (float(alt.values[0].num) / float(alt.values[0].den))
        else: 
            altitud = None
            
        return [latitud, longitud, altitud]

@st.cache_data
def base_map(coord=[40,3], zoom = 5):
    m = folium.Map(location=coord, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', zoom_start = zoom, max_zoom = 20)
    Fullscreen().add_to(m)

    return m

def base_leaflet_map(): 
    m = leafmap.Map()
    
    m.add_tile_layer(
        url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        name='Esri World Imagery',
        attribution='&copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
    )

    return m

@st.cache_data
def draw_map_leaflet_test2(data):
    #leafmap.update_package()
    m = base_leaflet_map()
    df = pd.DataFrame(data)
    m.add_points_from_xy(df, x='longitude', y='latitude', marker_cluster=True)
    #bounds = ipyleaflet.bounds_from_points(coordinates)
    #m.fit_bounds(bounds)
    map_html = m.to_html()
    with open('map.html', 'w') as f:
        f.write(map_html)

@st.cache_data
def min_max(coordinates):
    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]

    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)
    
    return [min_lat, max_lat, min_lon, max_lon]
    
def draw_map2():
    m = base_map()
    
    if st.session_state.get("test2"):
        coordinates = [
            (item["latitude"], item["longitude"])
            for item in st.session_state["test2"]
            if not pd.isna(item["latitude"]) and not pd.isna(item["longitude"])
        ]
        
        st.session_state["bounds"] = min_max(coordinates)
    
        if coordinates:
            FastMarkerCluster(data=coordinates).add_to(m)

        bounds = [[st.session_state["bounds"][0], st.session_state["bounds"][2]], [st.session_state["bounds"][1], st.session_state["bounds"][3]]]     
        m.fit_bounds(bounds)

    st_folium(m, key="user-map-visual", width=1200, height=800)
    
def extract_photos(path):
    counter = 0
    archivos = [f for f in os.listdir(path) if f.lower().endswith('.jpg')]
    total_archivos = len(archivos)
    
    if total_archivos == 0:
        st.sidebar.error(f"No .jpg files found in the directory: {path}")
        return

    if path != st.session_state["path"]:
        progress_bar = st.progress(0)
        progress_text = st.empty()
    
    for archivo in os.listdir(path):
        if archivo.lower().endswith('.jpg'):
            archivo_path = os.path.join(path, archivo)
            with open(archivo_path, 'rb') as file:
                nombre = "waypoint" + str(counter)
                data = extract_exif_from_uploaded_file(file)
                st.session_state["photos"].append([archivo_path, archivo, data])
                data_set = {
                    "name": archivo,
                    "latitude": data[0],
                    "longitude": data[1],
                    "altitud": data[2]
                }
                st.session_state["markers_set_path"].append(create_marker(data_set, "blue"))
                st.session_state["test2"].append(data_set)

                counter += 1
                
            if path != st.session_state["path"]:
                progress = min((counter / total_archivos), 1.0)  # Asegúrate de que esté entre 0.0 y 1.0
                progress_bar.progress(progress)
                progress_text.text(f"Processing: {int(progress * 100)}%")  # Mostrar porcentaje
    
    if path != st.session_state["path"]:
        progress_bar.progress(100)
        progress_text.text("Processing: 100%")
        progress_bar.empty()
        
    st.session_state["path"] = path
    
def review_path():
    c1,ca, c2 = st.columns([0.39, 0.02, 0.59])
    externo = st.sidebar.toggle("Check""(Trayectorias)")
    full_externo = st.sidebar.toggle("Check" "(Other path)")
    clear_all = st.sidebar.button("CLEAR")
    st.write(" ")

    if clear_all: 
        st.session_state["photos"].clear()
        st.session_state["markers_set_path"].clear()
        st.session_state["test2"].clear()
        st.session_state["path"] = "empty"

    elif externo:
        st.error("UNDER DEVELOPMENT")

    elif full_externo: 
        st.sidebar.write("---")
        path = st.sidebar.text_input("Specify the folder path")
        drop = st.sidebar.button("search")
        st.sidebar.write("---")
        map_2D = st.sidebar.button("MAP 2D +")

        if "test2" in st.session_state and map_2D:
                draw_map_leaflet_test2(st.session_state["test2"])
                webbrowser.open_new_tab('file://' + os.path.realpath("map.html"))
        
        if path and drop: 
            extract_photos(path)

    if externo or full_externo: 
        with c2:
            if st.session_state["photos"]:
                st.markdown("""
                <div style="text-align: center;">
                    <h4>TRAJECTORY </h4>
                </div>
                """, unsafe_allow_html=True)
                draw_map2()
  
        with c1:
            st.markdown("""
            <div style="text-align: center;">
                <h4>DATA </h4>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"TOTAL FILES: {len(st.session_state["photos"]) if st.session_state["photos"] else 0}")

            s1, s2 = st.columns(2, vertical_alignment="bottom")
            with s1:
                option = st.text_input('SELECT FILE')
                cleaned_option = option.replace(' ', '')
                
            if st.session_state["photos"]:
                for photo, nombre, data in st.session_state["photos"]:
                    if nombre == cleaned_option:
                        with open(photo, 'rb') as file:
                            image = Image.open(file)
                            st.image(image, caption=f'{nombre}', use_column_width=True)
                            
                            st.write("GPS metadata: ")
                            st.write("LAT: ", data[0], "LON: ", data[1], "ALT: ", data[2])
                        break
            else: 
                if not st.session_state["photos"]:
                    st.info("No photos uploaded yet")

def main():
    prepare_data()
    selected = menu()
    rutas = prepare_data_routes()
    ok = ready(rutas)

    if ok == True:
        if selected == "TRACK 🚀":
            display()
        if selected == "REVIEW FLIGHT PATH 🗺️":
            review_path() 
        if selected == "INFO  ℹ️":
            info()
    else:
        st.sidebar.info("NOT TRAJECTORIES AVAILABLE YET")

main()