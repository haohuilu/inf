import dash
from dash import callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
from datetime import date
import pandas as pd
from dash import dcc, html
import dash_table
from dash_table.Format import Format
import dash_bootstrap_components as dbc

bit = pd.read_csv("BIT.csv")
defensive = pd.read_excel('defensive details.xlsx', sheet_name='similar_pairs_defensive_all')
neutral = pd.read_excel('neutral details.xlsx', sheet_name='similar_pairs_neutral_all')
offensive = pd.read_excel('offensive details.xlsx', sheet_name='similar_pair_offensive_all')

df1_defensive = defensive
df1_neutral = neutral
df1_offensive =offensive

df2 = bit[["BIT_ID", "Country 1", "Country 2", "Year"]]

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_table
from dash_table.Format import Format
import dash_bootstrap_components as dbc

# Sample data initialization

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.layout = html.Div([
    # Outermost Container
    html.Div([
        # Header with Logo and Title
        html.Div([
            html.Img(src='/assets/1.png', id='logo', style={'height': '80px'}),
            html.H2('National influence in clause dissemination for safeguarding health across BITs', style={'marginLeft': '20px'})
        ], style={'display': 'flex', 'alignItems': 'center', 'background': '#f4f4f4', 'borderBottom': 'solid 1px #ddd', 'padding': '10px'}),
        
        # Main Content Container
        html.Div([
            # Left Side
            html.Div([
                html.Div([
                    html.P([
                        "Demo Video: ",
                        html.A("http://video.inftool.com", href="http://video.inftool.com", target="_blank"),  # Hyperlink to Demo Video
                        html.Br(),
                        "Chatbot (beta): ",
                        html.A("http://chatbot.inftool.com", href="https://chatbot.inftool.com", target="_blank")  # Hyperlink to Chatbot
                    ], style={'marginBottom': '20px', 'fontSize': '14px'})
                ], style={'padding': '10px 0'}),  # Spacer to move the content down
                dcc.RadioItems(
                    options=[
                        {'label': ' Defensive', 'value': 'defensive'},
                        {'label': ' Neutral', 'value': 'neutral'},
                        {'label': ' Progressive', 'value': 'offensive'},
                    ],
                    value='defensive',
                    id='strategy-selection',
                    style={'marginBottom': '20px'}
                ),
                html.Div([
                    html.Label("Similarity Range:"),
                    dcc.Input(id='similarity-start-input', type='number', value=0, step=0.01, style={'marginRight': '10px'}),
                    dcc.Input(id='similarity-end-input', type='number', value=1, step=0.01)
                ], style={'marginTop': '10px'}),
                html.Div([
                    html.Label("Year Range:", style={'marginTop': '20px'}),
                    dcc.Input(id='year-start-input', type='number', value=1959, style={'marginRight': '10px'}),
                    dcc.Input(id='year-end-input', type='number', value=2022)
                ], style={'marginTop': '10px'}),
                html.Div([
                    dbc.Button("Calculate", id="calculate-button", color="primary", className="mt-2")
                ], style={'marginTop': '20px'}), 
                html.Div([
                    html.P("Researchers using this tool for research should cite the following article:", style={'fontStyle': 'italic'}),
                    html.P([
                        "Uddin, S., Lu, H., Alschner, W., Patay, D., Frank, N., Gomes, F.S., and Thow, A.M., ",
                        html.I("An NLP-based novel approach for assessing national influence in clause dissemination across bilateral investment treaties"),  # Italicized title
                        ". Plos one, ",
                        html.B("19"),  # Bold volume number
                        "(3): p. e0298380.",
                    ], style={'marginBottom': '20px', 'fontSize': '14px'})
                ], style={'padding': '10px 0'}),
            ], style={'width': '25%', 'padding': '20px', 'borderRight': 'solid 1px #ddd'}),
        

            # Right Side
            html.Div([
                html.Div(id='major-role-card', className='card', style={'margin': '20px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'background': '#f9f9f9'}),
                html.Div(id='output-table', style={'margin': '20px'})
            ], style={'width': '75%', 'padding': '20px'})
        ], style={'display': 'flex', 'flexDirection': 'row'}),
    ], style={'maxWidth': '1200px', 'margin': '0 auto'}),  # This outermost container styling centralizes the content.
    
    html.Div([
        html.P("© 2023 The University of Sydney", style={'textAlign': 'center', 'margin': '20px', 'fontSize': '12px', 'color': '#999'})
    ], style={'borderTop': '1px solid #ddd', 'background': '#f4f4f4'}),
])

@app.callback(
    [Output('output-table', 'children'),
     Output('major-role-card', 'children')],
    [Input('calculate-button', 'n_clicks')],
    [State('similarity-start-input', 'value'),
     State('similarity-end-input', 'value'),
     State('year-start-input', 'value'),
     State('year-end-input', 'value'),
     State('strategy-selection', 'value')]
)

def update_table(n, sim_start, sim_end, year_start, year_end, strategy):    # ... (the callback remains unchanged)

    # Choosing dataframe based on selected strategy
    if strategy == 'defensive':
        chosen_df1 = df1_defensive
    elif strategy == 'neutral':
        chosen_df1 = df1_neutral
    else:
        chosen_df1 = df1_offensive

    # Filter dataframes based on inputs
    filtered_df1 = chosen_df1[(chosen_df1['similarity'] >= sim_start) & (chosen_df1['similarity'] <= sim_end)]
    filtered_df2 = df2[(df2['Year'] >= year_start) & (df2['Year'] <= year_end)]

    # Frequency of Unique BIT
    freq_df = pd.concat([filtered_df1['BIT1'], filtered_df1['BIT2']]).value_counts().reset_index()
    freq_df.columns = ['BIT_ID', 'Frequency']

    # Weight column
    total_freq = freq_df['Frequency'].sum()
    freq_df['Weight'] = freq_df['Frequency'] / total_freq

    # Aggregate weight by country
    agg_df = pd.merge(freq_df, filtered_df2, on='BIT_ID', how='inner')
    country_weight = pd.concat([agg_df[['Country 1', 'Weight']], agg_df[['Country 2', 'Weight']].rename(columns={'Country 2': 'Country 1'})])
    country_weight_agg = country_weight.groupby('Country 1')['Weight'].sum().reset_index().sort_values(by='Weight', ascending=False)
    country_weight_agg['Weight'] = country_weight_agg['Weight'].round(4)

    # Rename the column 'Country 1' to 'Country'
    country_weight_agg.rename(columns={'Country 1': 'Country'}, inplace=True)
    
    if country_weight_agg.empty:
        card_content = [html.H4("No Info Available")]
        table = html.Div(["No information available for the selected year(s)."])
        return table, card_content

    # Card for highest country by weight
    highest_country = country_weight_agg.iloc[0]
    card_content = [
        html.H4('Who plays the major role?'),
        html.H2(highest_country['Country']),
        html.P(f"Weight: {highest_country['Weight']:.4f}")
    ]

    # Using DataTable for paginated display
    table = dash_table.DataTable(
        columns=[
            {"name": "Country", "id": "Country"},
            {"name": "INF Weight", "id": "Weight", "type": "numeric", "format": Format(precision=4)}
        ],
        data=country_weight_agg.to_dict('records'),
        page_size=100,
        style_table={'height': '400px', 'overflowY': 'auto'},     
        style_header={
            'fontWeight': 'bold',
            'color': 'black',
            'border': '1px solid black',
            'textAlign': 'center'  # Centering header text
        },
        style_cell={
            'textAlign': 'center'  # Centering cell text
        }
    )

    return table, card_content




def on_calculate_button_click(n_clicks, sim_start, sim_end, year_start, year_end, strategy):
    return update_table(n_clicks, sim_start, sim_end, year_start, year_end, strategy)

    
    # ... (the callback remains unchanged)
    
    # Choosing dataframe based on selected strategy
    if strategy == 'defensive':
        chosen_df1 = df1_defensive
    elif strategy == 'neutral':
        chosen_df1 = df1_neutral
    else:
        chosen_df1 = df1_offensive

    # Filter dataframes based on inputs
    filtered_df1 = chosen_df1[(chosen_df1['similarity'] >= sim_start) & (chosen_df1['similarity'] <= sim_end)]
    filtered_df2 = df2[(df2['Year'] >= year_start) & (df2['Year'] <= year_end)]

    # Frequency of Unique BIT
    freq_df = pd.concat([filtered_df1['BIT1'], filtered_df1['BIT2']]).value_counts().reset_index()
    freq_df.columns = ['BIT_ID', 'Frequency']

    # Weight column
    total_freq = freq_df['Frequency'].sum()
    freq_df['Weight'] = freq_df['Frequency'] / total_freq

    # Aggregate weight by country
    agg_df = pd.merge(freq_df, filtered_df2, on='BIT_ID', how='inner')
    country_weight = pd.concat([agg_df[['Country 1', 'Weight']], agg_df[['Country 2', 'Weight']].rename(columns={'Country 2': 'Country 1'})])
    country_weight_agg = country_weight.groupby('Country 1')['Weight'].sum().reset_index().sort_values(by='Weight', ascending=False)

    # Rename the column 'Country 1' to 'Country'
    country_weight_agg.rename(columns={'Country 1': 'Country'}, inplace=True)
    
    if country_weight_agg.empty:
        card_content = [html.H4("No Info Available")]
        table = html.Div(["No information available for the selected year(s)."])
        return table, card_content

    # Card for highest country by weight
    highest_country = country_weight_agg.iloc[0]
    card_content = [
        html.H4('Who plays the major role?'),
        html.H2(highest_country['Country']),
        html.P(f"Weight: {highest_country['Weight']:.4f}")
    ]

    # Using DataTable for paginated display
    table = dash_table.DataTable(
        columns=[
            {"name": "Country", "id": "Country"},
            {"name": "INF Weight", "id": "Weight", "type": "numeric", "format": Format(precision=4)}
        ],
        data=country_weight_agg.to_dict('records'),
        page_size=10,
        style_table={'height': '400px', 'overflowY': 'auto'},     
        style_header={
            'fontWeight': 'bold',
            'color': 'black',
            'border': '1px solid black',
            'textAlign': 'center'  # Centering header text
        },
        style_cell={
            'textAlign': 'center'  # Centering cell text
        }
    )

    return table, card_content

if __name__ == '__main__':
    app.run_server()
