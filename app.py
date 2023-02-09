import plotly.graph_objects as go # or plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import threading
from HandGestureTracker import *
import pandas as pd
import os

from dash import html, dcc, callback, Input, Output, State, ctx
# import plotly.express as px
# df = px.data.gapminder().query("year == 2007")

#,'./assets/'

dataset_path = './datasets/'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) #__name__, use_pages=True, 

'''class CustomThread(threading.Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        threading.Thread.__init__(self,daemon=True)
        # set a default value
        self.value = None

    # function executed in a new thread
    def run(self):
        # block for a moment
        time.sleep(1)
        # store data in an instance variable
        self.value = {'dX':tracker.get_last_delta_x(), 
                'dY':tracker.get_last_delta_x(),
                'gestures':tracker.get_last_gesture()}'''

df1 = pd.read_csv('./datasets/cleaned_merge.csv')

overlays = {
    'Percent of Women in Agriculture Sector': (df1['f_agri'], df1['Longitude'],df1['Latitude'], 'Percentage of Women' ),
    'Percent of Women in Manufacturing Sector': (df1['f_sec'], df1['Longitude'],df1['Latitude'], 'Percentage of Women' ),
    'Percent of Women in Services Sector': (df1['f_ser'], df1['Longitude'],df1['Latitude'], 'Percentage of Women' ),
}

fig = go.Figure(data=go.Scattergeo(
        locationmode = 'ISO-3',
        lon = df1['Longitude'],
        lat = df1['Latitude'],
        text = df1['f_agri'],
        mode = 'markers',
        hovertext=[f"Percent of Women Working in Agriculture Sector: {df1['f_agri'].iloc[i]}<br>Percent of Women Working in Manufacturing Sector (%): {df1['f_sec'].iloc[i]}<br>Percent of Women Working in Service Sector (%): {df1['f_ser'].iloc[i]}<br> GDP per Capita: {df1['GDP per Capita'].iloc[i]}<br>Unemployment: {df1['UNEMPR'].iloc[i]}<br>Urbanization rate: {df1['Urbanization rate'].iloc[i]}<br>Population growth: {df1['Population growth'].iloc[i]}<br>Life expectancy: {df1['Life expectancy'].iloc[i]}<br>Fertility: {df1['Fertility'].iloc[i]}" for i in range(df1.shape[0])],
        marker = dict(
            size = df1['Urbanization rate'].fillna(1)/3,
            opacity = 0.8,
            reversescale = True,
            autocolorscale = True,
            #symbol = 'square',
            line = dict(
                width=0.5,
                color='rgba(102, 102, 102)'
            ),
            colorscale = 'Blues',
            cmin = 0,
            color = df1['Urbanization rate'].fillna(1)/3,
            cmax = (df1['Urbanization rate'].fillna(1)/3).max(),
            colorbar_title="Urbanization rate"
        )))

fig.update_geos(projection_type="orthographic")#,geo = dict(scope='world')

fig.update_layout(
                height=900,
                width=1200,
                margin={
                        "r":0,
                        "t":5,
                        "l":0,
                        "b":5
                        })

fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
},geo=dict(bgcolor= 'rgba(0,0,0,0)'))

fig.update_geos(
    resolution=110,
    showcoastlines=False, coastlinecolor="RebeccaPurple",
    showland=True, landcolor="#08b549",
    showocean=True, oceancolor="#6b7ae7",
    showlakes=False, lakecolor="Blue",
    showcountries=True, countrycolor="White",
    showrivers=False, rivercolor="Blue",
)

storage = html.Div([
    dcc.Store(id="Xpos", storage_type='session'),
    dcc.Store(id="Ypos", storage_type='session'),
    dcc.Store(id="Zpos", storage_type='session')
])



app.layout = html.Div([
    # navbar
    dbc.NavbarSimple( 
        children=[
            
            html.Div(id='current_coords'),
            html.Button('up', id='up_btn', n_clicks=0),
            html.Button('down', id='d_btn', n_clicks=0),
            html.Button('left', id='l_btn', n_clicks=0),
            html.Button('right', id='r_btn', n_clicks=0)
        ],
        brand_href="#",
        color="dark",
        dark=True,
    ),
    # graph
    html.Div(id='camera-data'),
    #html.Div(dcc.Dropdown([feature for feature in overlays.keys()], list(overlays.keys())[0], id='demo-dropdown')),
    html.Center(children=[dcc.Graph(figure=fig, id='globe')]), 

    # storage
    #storage, 

    # update component
    dcc.Interval(
            id='interval-component',
            interval=10, # in milliseconds
            n_intervals=0)
    ],
    style={'backgroundColor': 'black',
            'background-image': 'url("./assets/lazy_dynamic.gif")',
            'background-size': '100%',
            'position': 'fixed',
            'width': '100%',
            'height': '100%'})


## update map overlay

# @app.callback(
#     Output('globe', 'figure'),
#     Input('demo-dropdown', 'value'),
#     Input('globe', 'figure')
# )
# def update_output(value, fig):
    
#     overlay_name = value
#     overlay_data = overlays[value][0]
#     lon = overlays[value][1]
#     lat = overlays[value][2]
#     scale_label = overlays[value][3]

#     print(overlay_name)

#     fig.add_trace(data=go.Scattergeo(
#             locationmode = 'ISO-3',
#             lon = lon,
#             lat = lat,
#             text = overlay_data,
#             mode = 'markers',
#             #hovertext=[df1['f_agri']],
#             hovertemplate=[f'{overlay_name}: {v}' for v in overlay_data],
#             marker = dict(
#                 size = overlay_data/2,
#                 opacity = 0.8,
#                 reversescale = True,
#                 autocolorscale = True,
#                 #symbol = 'square',
#                 line = dict(
#                     width=0.5,
#                     color='rgba(102, 102, 102)'
#                 ),
#                 colorscale = 'Blues',
#                 cmin = 0,
#                 color = overlay_data,
#                 cmax = overlay_data.max(),
#                 colorbar_title=scale_label
#             )))

    # fig.update_geos(projection_type="orthographic")#,geo = dict(scope='world')

    # fig.update_layout(
    #                 height=900,
    #                 width=1200,
    #                 margin={
    #                         "r":0,
    #                         "t":5,
    #                         "l":0,
    #                         "b":5
    #                         })

    # fig.update_layout({
    #     'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    #     'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    # },geo=dict(bgcolor= 'rgba(0,0,0,0)'))

    # fig.update_geos(
    #     resolution=110,
    #     showcoastlines=False, coastlinecolor="RebeccaPurple",
    #     showland=True, landcolor="#08b549",
    #     showocean=True, oceancolor="#6b7ae7",
    #     showlakes=False, lakecolor="Blue",
    #     showcountries=True, countrycolor="White",
    #     showrivers=False, rivercolor="Blue",
    # )
    #return fig


@app.callback(
    Output('camera-data', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('globe', 'figure'))
def updateStateVariables(n, layout):
    layout2 = layout['layout']
    current_view = layout2['geo']['projection']
    if current_view.get('scale',None) == None:
        current_view['scale'] = 0.5
    else:
        pass

    return html.Span([str(current_view)],style={"color": "white"})

#### camera control callbacks

'''
html.Button('up', id='up_btn', n_clicks=0),
html.Button('down', id='d_btn', n_clicks=0),
html.Button('left', id='l_btn', n_clicks=0),
html.Button('right', id='r_btn', n_clicks=0),
html.Button('zin', id='zin_btn', n_clicks=0),
html.Button('zout', id='zout_btn', n_clicks=0)
'''
@app.callback(
    Output('globe', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('up_btn','n_clicks'),
    Input('d_btn','n_clicks'),
    Input('l_btn','n_clicks'),
    Input('r_btn','n_clicks'),
    Input('globe', 'figure')
)
def move(n, n_clicks_up, n_clicks_down, n_clicks_left, n_clicks_right, figure):
    layout = figure['layout']
    current_view = layout['geo']['projection']
    if current_view.get('rotation', None) == None:
        current_view['rotation'] = dict(lon=0, lat=0, roll=0)
    if current_view.get('scale', None) == None:
        current_view['scale'] = 0.5
    else:
        if 'up_btn' == ctx.triggered_id:
            current_view['rotation']['lat'] += 5
        elif 'd_btn' == ctx.triggered_id:
            current_view['rotation']['lat'] -= 5
        elif 'l_btn' == ctx.triggered_id:
            current_view['rotation']['lon'] -= 5
        elif 'r_btn' == ctx.triggered_id:
            current_view['rotation']['lon'] += 5
    
        else:

            dX, dY = tracker.get_last_delta_x(), tracker.get_last_delta_y()
            
            factor = 0.10

            gestures = tracker.get_last_gesture()
            #print(gestures)
            #print(current_view)
            if gestures != 0:
                if gestures[0] == gestures[-1] and gestures[0] == ' fist\n':
                    scaled_rotate_x = dX*factor
                    scaled_rotate_y = dY*factor
                    current_view['rotation']['lon'] -= scaled_rotate_x 
                    current_view['rotation']['lat'] -= scaled_rotate_y

        # elif gestures[0] == gestures[-1] and gestures[0] == ' peace\n':
        #     current_view['scale'] += dY

    return figure


# # custom thread
# class CustomThread(threading.Thread):
#     # constructor
#     def __init__(self):
#         # execute the base constructor
#         threading.Thread.__init__(self,daemon=True)
#         # set a default value
#         self.value = None

#     # function executed in a new thread
#     def run(self):
#         # block for a moment
#         time.sleep(1)
#         # store data in an instance variable
#         self.value = {'dX':tracker.get_last_delta_x(), 
#                 'dY':tracker.get_last_delta_x(),
#                 'gestures':tracker.get_last_gesture()}


# @app.callback(
#     Output('camera-data', 'figure'),
#     Input('interval-component', 'n_intervals'),
#     Input('globe', 'figure'))
# def gestureControl(n, figure):
#     layout = layout['layout']
#     current_view = layout['geo']['projection']
#     if current_view.get('rotation', None) == None:
#         current_view['rotation'] = dict(lon=0, lat=0, roll=0)
#     else:
#         pass
#     dX, dY = tracker.get_last_delta_x(), tracker.get_last_delta_y()
#     print(dX, dY)
#     current_view['rotation']['lon'] += dX
#     current_view['rotation']['lat'] += dY
#         #gestures = tracker.get_last_gesture()

#         # if gestures != 0:
#         #     if gestures[0] == gestures[-1] and gestures[0] == ' fist\n':
#         #         current_view['rotation']['lon'] += tracker.get_last_delta_x()
#         #         current_view['rotation']['lat'] += tracker.get_last_delta_y()
#         # else:
#         #     pass
#     return layout


def runserver():
    app.run_server(host= '0.0.0.0', debug=False)


if __name__ == '__main__':
    tracker = HandGestureTracker()
    dash_server_thread = threading.Thread(target=runserver, daemon=True)
    tracker_thread = threading.Thread(target=tracker.main, daemon=True)
    
    # app_runner_thread = threading.Thread(target=app_runner, daemon=False)
    
    dash_server_thread.start()
    tracker_thread.start()
    # app_runner_thread.start()

    dash_server_thread.join()
    tracker_thread.join()
    # app_runner_thread.join()




    #app.run_server(host= '0.0.0.0', debug=False)
