import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

def load_and_clean_data(file_path):
    data = pd.read_csv(file_path)
    for column in ['Total', 'Men', 'Women']:
        if column in data.columns:
            data[column] = data[column].astype(str).str.replace(',', '').str.replace('"', '')
            data[column] = pd.to_numeric(data[column], errors='coerce')
    data = data.dropna(subset=['Total', 'Men', 'Women'])
    return data

def get_essential_services_data(data):
    services = ['police', 'firefighter', 'nurse']
    pattern = '|'.join(services)
    service_data = data[data['Occupation'].str.contains(pattern, case=False, na=False)]
    return service_data

def get_noc_top_level_data(data):
    pattern = r'^\d\s[A-Za-z]+'
    top_level_data = data[data['Occupation'].str.match(pattern, na=False)]
    return top_level_data

def get_engineering_data(data):
    engineering_jobs = ['computer engineer', 'mechanical engineer', 'electrical engineer']
    pattern = '|'.join(engineering_jobs)
    engineering_data = data[data['Occupation'].str.contains(pattern, case=False, na=False)]
    return engineering_data

def get_province_data():
    province_info = {
        'Alberta': {'Population': 3375130},
        'British Columbia': {'Population': 4200425},
        'Manitoba': {'Population': 1058410},
        'New Brunswick': {'Population': 648250},
        'Newfoundland and Labrador': {'Population': 433955},
        'Northwest Territories': {'Population': 31915},
        'Nova Scotia': {'Population': 31915},
        'Nunavut': {'Population': 24540},
        'Ontario': {'Population': 11782825},
        'Prince Edward Island': {'Population': 126900},
        'Quebec': {'Population': 93585},
        'Saskatchewan': {'Population': 882760},
        'Yukon': {'Population': 32775}
    }
    return province_info

try:
    data = load_and_clean_data('data.csv')
except:
    data = pd.DataFrame()

province_data = get_province_data()
essential_service_data = get_essential_services_data(data)
noc_top_level_data = get_noc_top_level_data(data)
engineering_data = get_engineering_data(data)

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("2023 Canadian Employment Insight Dashboard", className="text-center"),
            html.P("Interactive visualization of employment statistics", className="text-center")
        ], width=12)
    ], className="mt-4 mb-4"),
    
    dbc.Tabs([
        dbc.Tab(label="Essential Services", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Essential Services Distribution", className="mt-3"),
                    html.P("Police, firefighters, and nurses across provinces")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select Service:"),
                    dcc.Dropdown(
                        id="service-type-dropdown",
                        options=[
                            {"label": "All Essential Services", "value": "all"},
                            {"label": "Police Officers", "value": "police"},
                            {"label": "Firefighters", "value": "fire"},
                            {"label": "Registered Nurses", "value": "nurse"}
                        ],
                        value="all",
                        clearable=False
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("View Mode:"),
                    dcc.RadioItems(
                        id="normalization-radio",
                        options=[
                            {"label": "Absolute Numbers", "value": "absolute"},
                            {"label": "Per 10,000 Population", "value": "normalized"}
                        ],
                        value="absolute",
                        inline=True
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Sort By:"),
                    dcc.Dropdown(
                        id="sort-dropdown",
                        options=[
                            {"label": "Province (A-Z)", "value": "province"},
                            {"label": "Count (High-Low)", "value": "count_desc"},
                            {"label": "Count (Low-High)", "value": "count_asc"}
                        ],
                        value="count_desc",
                        clearable=False
                    )
                ], width=4)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="essential-services-graph")
                ], width=12)
            ])
        ]),
        
        dbc.Tab(label="Gender Employment", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Gender Employment Statistics", className="mt-3"),
                    html.P("Top-level NOC category employment by gender")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select NOC Categories:"),
                    dcc.Dropdown(
                        id="noc-dropdown",
                        options=[{"label": occ, "value": occ} for occ in noc_top_level_data['Occupation'].unique()],
                        value=noc_top_level_data['Occupation'].unique()[:3].tolist(),
                        multi=True
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Chart Type:"),
                    dcc.RadioItems(
                        id="chart-type-radio",
                        options=[
                            {"label": "Stacked Bar", "value": "stack"},
                            {"label": "Grouped Bar", "value": "group"},
                            {"label": "Gender Ratio", "value": "ratio"}
                        ],
                        value="stack",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="gender-employment-graph")
                ], width=12)
            ])
        ]),
        
        dbc.Tab(label="Engineering Workforce", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Engineering Workforce", className="mt-3"),
                    html.P("Computer, mechanical, and electrical engineers by province")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Engineering Types:"),
                    dcc.Checklist(
                        id="engineering-checklist",
                        options=[
                            {"label": "Computer Engineers", "value": "computer"},
                            {"label": "Mechanical Engineers", "value": "mechanical"},
                            {"label": "Electrical Engineers", "value": "electrical"}
                        ],
                        value=["computer", "mechanical", "electrical"],
                        inline=True
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("View Mode:"),
                    dcc.RadioItems(
                        id="engineering-view-radio",
                        options=[
                            {"label": "Absolute Numbers", "value": "absolute"},
                            {"label": "Per 10,000 Population", "value": "per_capita"}
                        ],
                        value="absolute",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="engineering-manpower-graph")
                ], width=12)
            ])
        ]),
        
        dbc.Tab(label="Custom Insight", children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Occupation Hierarchy Analysis", className="mt-3"),
                    html.P("Gender distribution across occupation levels")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Label("Select Category:"),
                    dcc.Dropdown(
                        id="occupation-category-dropdown",
                        options=[
                            {"label": "Business & Finance", "value": "business"},
                            {"label": "Sciences & Engineering", "value": "science"},
                            {"label": "Health", "value": "health"},
                            {"label": "Education & Law", "value": "education"},
                            {"label": "Art & Culture", "value": "art"}
                        ],
                        value="science",
                        clearable=False
                    )
                ], width=6),
                
                dbc.Col([
                    html.Label("Analysis Type:"),
                    dcc.RadioItems(
                        id="analysis-type-radio",
                        options=[
                            {"label": "Hierarchy Level", "value": "hierarchy"},
                            {"label": "Gender Parity", "value": "parity"}
                        ],
                        value="hierarchy",
                        inline=True
                    )
                ], width=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="custom-insight-graph")
                ], width=12)
            ])
        ])
    ]),
    
    html.Footer([
        html.P("Data Source: 2023 Statistics Canada Census", className="text-center mt-4 text-muted")
    ])
], fluid=True)

# Callbacks remain unchanged
