#Lucas Martínez Rodríguez - Eiffage

#IMPORTANTE: 
#DAR PERMISOS AL DIRECTORIO DE LECTURA, ESCRITURA Y EJECUCIÓN !!!
#CUIDADO AL PARSEAR CON LOS ESPACIOS DE NOMBRE DEL ARCHIVO ¡¡¡
#CUIDADO CON LOS ARCHIVOS QUE SE PARSEAN (XML.etree no tiene ningún tipo de forma de detectar intenciones maliciosas dentre de un kml)
#Al INICIAR EL PROGRAMA TO DO LO QUE NO SEA UNA CARPETA DEL MISMO SE BORRA DEL DIRECTORIO¡¡¡

import folium.map
import folium, os, time, simplekml
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
import zipfile

#Directorio del workspace 
dirname = os.path.dirname(__file__)

#Out of pages
parent_dir = os.path.dirname(dirname)

routes_path = os.path.join(parent_dir, "Trayectorias")
path = os.path.join(parent_dir, "data", "rutas.csv")

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

def draw_traj(save = None):
    lat = 40.463667
    lon = -0.74922
    filepath = os.path.join(routes_path, st.session_state["name"], "waypoints.csv")
    way_df = pd.read_csv(filepath)
    mapa2 = folium.Map(location=[lat, lon], tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', zoom_start=5.5)
    
    if not way_df.empty:
        fg_waypoints = folium.FeatureGroup(name="Waypoints")
        fg_line = folium.FeatureGroup(name="Line")
        iteraciones = 0
        points = []
        for _, landmark in way_df.iterrows():
            points.append([landmark['latitude'], landmark['longitude']])
            if iteraciones == 0:         
                folium.Marker([landmark['latitude'], landmark['longitude']], popup=landmark['name'], icon=folium.Icon(icon = 'star',color='red')).add_to(fg_waypoints) 
            
            else:
                if iteraciones == len(way_df)-1:
                    folium.Marker([landmark['latitude'], landmark['longitude']], popup=landmark['name'], icon=folium.Icon(icon = 'star',color='green')).add_to(fg_waypoints) 

                else: 
                    folium.Marker([landmark['latitude'], landmark['longitude']], popup=landmark['name'], icon=folium.Icon(color='orange')).add_to(fg_waypoints) 

            iteraciones += 1

        folium.PolyLine(points,color="blue",weight=1.5,opacity=1).add_to(fg_line)    
        
        mapa2.add_child(fg_waypoints)
        mapa2.add_child(fg_line)
        folium.LayerControl().add_to(mapa2)
        mapa2.fit_bounds(mapa2.get_bounds())
        Fullscreen().add_to(mapa2)
    st.session_state["mapa2"] = mapa2

    if save == 1: 
        return mapa2
    
    st_folium(mapa2,key="traj-map",returned_objects=[],width=850, height=700)

def convert_df(data, filepath):
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    mapa_path = os.path.join(routes_path, st.session_state["name"], st.session_state["name"]+".html")
    kml_path = os.path.join(routes_path, st.session_state["name"], st.session_state["name"]+".kmz")
    os.remove(mapa_path)
    os.remove(kml_path)
    mapa = draw_traj(1)
    mapa.save(mapa_path)
    create_kml(st.session_state["name"])

def create_kml(route_name):
    filepath = os.path.join(routes_path, route_name, "waypoints.csv")
    waypoints = pd.read_csv(filepath)
    kml = simplekml.Kml()
    kml_file = os.path.join(routes_path, route_name, "{0}.kml".format(route_name))
    kmz_file = os.path.join(routes_path, route_name, "{0}.kmz".format(route_name))
    
    for index, row in waypoints.iterrows():
        name = str(row['name'])
        lon = float(row['longitude'])
        lat = float(row['latitude'])
        alt = float(row['altitud'])
        asl = float(row['ASL'])
        
        # Crear un punto en el KML
        newpoint = kml.newpoint(name=name, coords=[(lon, lat, (alt+asl))])
        newpoint.altitudemode = simplekml.AltitudeMode.absolute
    
    coords = [(float(row['longitude']), float(row['latitude']), (float(row['altitud']) + float(row['ASL']))) for index, row in waypoints.iterrows()]
    kml.newlinestring(name=route_name, coords=coords, altitudemode=simplekml.AltitudeMode.absolute)
    
    kml.save(kml_file)
    
    with zipfile.ZipFile(kmz_file, 'w', zipfile.ZIP_DEFLATED) as kmz:
        kmz.write(kml_file, os.path.basename(kml_file))
        
def data_uploader(name):
    filepath = os.path.join(routes_path, name, "waypoints.csv")
    try:
        df = pd.read_csv(filepath)
    except:
        df = pd.DataFrame()
        
    return df, filepath

def increment_key():
    st.session_state["key2"] += 1

def AG_table(): 
    df, filepath = data_uploader(st.session_state["name"])
    z1, z2, z3, z4 = st.columns(4)
    with z1:
        _funct = st.radio('Options', options=['Display', 'Delete'])
        
    gd = GridOptionsBuilder.from_dataframe(df)

    #JavaScript injection
    cell_button_add = JsCode('''
    class BtnCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <span>
                <style>
                .btn_add {
                    background-color: #71DC87;
                    border: 2px solid black;
                    color: #D05732;
                    text-align: center;
                    display: inline-block;
                    font-size: 12px;
                    font-weight: bold;
                    height: 2em;
                    width: 10em;
                    border-radius: 12px;
                    padding: 0px;
                }
                </style>
                <button id='click-button' 
                    class="btn_add" 
                    >&#x2193; Add</button>
            </span>
        `;
        }

        getGui() {
            return this.eGui;
        }
    };
    ''')
    
    js_add_row = JsCode('''
        function(e){
            let api = e.api;
            let rowPos = e.rowIndex + 1;
            api.applyTransaction({addIndex: rowPos, add: [{}]})
        };
        '''
        )
    
    js_delete_row = JsCode("""
        function(e) {
            let api = e.api;
            let sel = api.getSelectedRows();
            api.applyTransaction({remove: sel})
        };
        """)
    
    if _funct == 'Display':
        with z3:
            sel_mode = st.selectbox('Edit', options=['longitude', 'latitude', 'altitud'])
        
        with z2: 
            select_all = st.toggle("Select All Rows")
            
        with z4:
            entero = st.number_input("new value:", key='drop')
            drop = float(entero)
       
        gd.configure_column(field='🔧', editable=False, filter=False,
                            onCellClicked=js_add_row, cellRenderer=cell_button_add,
                            autoHeight=True, wrapText=True)
            
        gd.configure_pagination(enabled=False)
        gd.configure_default_column(editable=True, groupable=True)

        if select_all:
            gd.configure_selection(selection_mode='multiple', use_checkbox=True, pre_selected_rows=df.index.tolist())  
        else:
            gd.configure_selection(selection_mode='multiple', use_checkbox=True)  

        gridoptions = gd.build()
        
        with st.form('table') as f:
            grid_table = AgGrid(df, gridOptions=gridoptions,
                                width="100%",
                                editable=True,
                                allow_unsafe_jscode = True,
                                theme = 'streamlit',
                                height = 550,
                                fit_columns_on_grid_load = True, 
                                )
            st.write(" *Note: Don't forget to hit enter ↩ on new entry.*")
            sel_row = grid_table["selected_rows"]
            done = st.form_submit_button("Confirm change(s) 🔒", type="primary")

            if done: 
                if drop and sel_mode:
                    for index in sel_row:
                        indice = index['_selectedRowNodeInfo']['nodeRowIndex']
                        if indice is not None: 
                            grid_table["data"].loc[indice, sel_mode] = drop
                increment_key()
                convert_df(grid_table['data'], filepath)

    if _funct == 'Delete':
        gd.configure_selection('single')
        gd.configure_grid_options(onRowSelected=js_delete_row, pre_selected_rows=[])
        gridoptions = gd.build()

        with st.form('table') as f:
            grid_table = AgGrid(df, gridOptions=gridoptions, key='AgGrid2',
                                width="100%",
                                allow_unsafe_jscode=True,
                                enable_enterprise_modules=True,
                                fit_columns_on_grid_load=True,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                reload_data=True,
                                theme='streamlit',
                                height=550)
            st.write(" *Touch any row to delete*")
            done = st.form_submit_button("Confirm change(s) 🔒", type="primary")
            if done: 
                convert_df(grid_table['data'], filepath)
                        
def display():
    c2,cb, c3 = st.columns([0.49, 0.02, 0.49])
              
    with c2:
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>TRAJECTORY {st.session_state["name"]}</h4>
        </div>
        """, unsafe_allow_html=True)
        #st.components.v1.html(data[2], height=500)
        
        st.fragment(draw_traj, run_every=1.0)() 
            
    with c3:
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>WAYPOINTS DATA</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.fragment(AG_table, run_every=1.5)()
        
def edit_data():
    c1, ca, c2,cb, c3 = st.columns([0.14, 0.02, 0.35,0.02, 0.47])
    
    with c1:
        st.markdown("""
        <div style="text-align: center;">
            <h4>TOOLBAR 🛠️</h4>
        </div>
        """, unsafe_allow_html=True) 

def info(): 
    st.info("UNDER DEVELOPMENT")

def menu():    
    over_theme = {
        'menu_background': ' #d5d5d5 ', 
        'menu_font_size': '24px',         
        'border_width': '2px',        
        'icon_size': '24px '
    }    
    
    datos = [
    {'label':"EDIT TRAJECTORY 🗺️"},
    {'label':"EDIT DATA 💿"},
    {'label':"INFO  ℹ️"},
    ]

    menu_id = hc.nav_bar(menu_definition=datos,
                        override_theme=over_theme,
                        key="menu4454") 

    return menu_id

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

@st.cache_data
def prepare_data():
    if "name" not in  st.session_state:
        st.session_state["name"] = []
        
    if "key2" not in  st.session_state:
        st.session_state["key2"] = 0
        
    if "waypoints" not in  st.session_state:
        st.session_state["waypoints"] = []
        
    if "excell" not in  st.session_state:
        st.session_state["excell"] = 0
        
    if "map" not in  st.session_state:
        st.session_state["map"] = 0
        
    if "key_select" not in st.session_state:
        st.session_state["key_select"] = 1
        
def main():
    prepare_data() 
    searching_trajectories()
    selected = menu()

    rutas = prepare_data_routes()
    ok = ready(rutas)
    
    if ok == True:
        if selected == "EDIT TRAJECTORY 🗺️":
            display()
        if selected == "EDIT DATA 💿":
            edit_data()
        if selected == "INFO  ℹ️":
            info()
    else:
        st.sidebar.info("NOT TRAJECTORIES AVAILABLE YET")
        
main()
    
    
    
