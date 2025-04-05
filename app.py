# Dash Dashboard for Census Visualization (Google Colab Setup)

!pip install dash dash-bootstrap-components jupyter-dash --quiet

import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from jupyter_dash import JupyterDash

# Load the dataset
df = pd.read_csv('/mnt/data/data.csv')

# Preprocess the data: remove commas and convert numeric columns to int
df[['Total', 'Men', 'Women']] = df[['Total', 'Men', 'Women']].replace({',': ''}, regex=True).astype(int)

# Extract major NOC groups (first digit only)
df['NOC_Code'] = df['Occupation'].str.extract(r'^(\d)')

# Initialize the app
app = JupyterDash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

app.layout = html.Div([
    html.H1("Canada 2023 Census Dashboard", className="text-center my-4"),

    # Gender distribution bar chart
    html.Div([
        html.H4("Employment by Gender"),
        dcc.RadioItems(
            id='gender-radio',
            options=[
                {'label': 'Total', 'value': 'Total'},
                {'label': 'Men', 'value': 'Men'},
                {'label': 'Women', 'value': 'Women'}
            ],
            value='Total',
            inline=True
        ),
        dcc.Graph(id='gender-bar')
    ], className="mb-5"),

    # NOC Group distribution
    html.Div([
        html.H4("Employment by NOC Group (1-digit code)"),
        dcc.Dropdown(
            id='noc-dropdown',
            options=[
                {'label': f'NOC {code}', 'value': code}
                for code in sorted(df['NOC_Code'].dropna().unique())
            ],
            value='1',
            clearable=False
        ),
        dcc.Graph(id='noc-bar')
    ], className="mb-5"),

    # Engineers employment
    html.Div([
        html.H4("Engineer-Related Occupations"),
        dcc.Graph(id='engineer-bar', figure=px.bar(
            df[df['Occupation'].str.contains("engineer", case=False)],
            x='Occupation', y='Total',
            title="Engineer Occupations (Total)",
            labels={'Total': 'Total Employment'},
            height=500
        ))
    ], className="mb-5"),

    # Custom insight chart (Top 10 occupations)
    html.Div([
        html.H4("Top 10 Occupations by Employment"),
        dcc.Graph(id='top10-bar', figure=px.bar(
            df.sort_values(by='Total', ascending=False).head(10),
            x='Occupation', y='Total',
            title="Top 10 Occupations in Canada (2023)",
            labels={'Total': 'Total Employment'},
            height=500
        ))
    ])
])

# Callbacks
@app.callback(
    Output('gender-bar', 'figure'),
    Input('gender-radio', 'value')
)
def update_gender_chart(selected_gender):
    fig = px.bar(
        df.sort_values(by=selected_gender, ascending=False).head(15),
        x='Occupation', y=selected_gender,
        title=f"Top 15 Occupations by {selected_gender}",
        labels={selected_gender: f"{selected_gender} Count"},
        height=500
    )
    return fig

@app.callback(
    Output('noc-bar', 'figure'),
    Input('noc-dropdown', 'value')
)
def update_noc_chart(noc_digit):
    filtered = df[df['NOC_Code'] == noc_digit]
    fig = px.bar(
        filtered.sort_values(by='Total', ascending=False),
        x='Occupation', y='Total',
        title=f"Occupations in NOC Group {noc_digit}",
        labels={'Total': 'Total Employment'},
        height=500
    )
    return fig

# Run the app
app.run_server(mode='inline', debug=False)

# Add this to the first cell of your notebook:
# [Video Demo Link Here]  <-- Replace with actual link when ready
