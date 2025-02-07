import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import PATHS
from indicators import (
    calculate_sma,
    calculate_bollinger_bands,
    calculate_peak_offpeak_spread
)

### DATA ###
df = pd.read_csv(PATHS['downloads']['price_data'])
df['FECHA'] = pd.to_datetime(df['FECHA']) #convert the fecha column to a datetime object

#create a new column with the datetime of the fecha and hora in format YYYY-MM-DD HH:MM:SS
df['DATETIME'] = pd.to_datetime(df['FECHA'].astype(str) + ' ' + df['HORA'].astype(str) + ':00:00')
df = df.sort_values('DATETIME') #sort the dataframe by the datetime column

###### Initialize the Dash app with external stylesheets ######
###########################
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap'
    ]
)

# Define custom styles
COLORS = {
    'primary': '#4AD7D4',
    'secondary': '#00B2AF',
    'background': '#f8fafc',
    'grid': '#e2e8f0',
    'text': '#1e293b',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444'
}

### LAYOUT ###
app.layout = html.Div([

    # Main container
    html.Div([
        # Header section
        html.Div([
            html.H1('Análisis del Precio Spot de Electricidad en España', 
                   style={
                       'textAlign': 'center',
                       'color': COLORS['text'],
                       'fontSize': '2.5rem',
                       'fontWeight': '700',
                       'marginBottom': '0.5rem',
                       'fontFamily': 'Plus Jakarta Sans, sans-serif'
                   }),
            html.P('Datos disponibles desde el 01/01/2020 hasta el 04/02/2025',
                  style={
                      'textAlign': 'center',
                      'color': COLORS['secondary'],
                      'fontSize': '1.1rem',
                      'marginBottom': '1rem',
                      'fontFamily': 'Inter, sans-serif'
                  })
        ], style={'padding': '2rem 0'}),
        
        # Quick timeframe selector
        html.Div([ #buttons to select the timeframe of the data to be displayed (1 day, 1 week, 1 month, 3 months, 6 months, 1 year, max)
            html.Button('1D', id='1d-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('1S', id='1w-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('1M', id='1m-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('3M', id='3m-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('6M', id='6m-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('1A', id='1y-button', n_clicks=0,
                       className='timeframe-button'),
            html.Button('MAX', id='max-button', n_clicks=0,
                       className='timeframe-button'),
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'gap': '1rem',
            'marginBottom': '2rem'
        }),
        
        # Controls and Stats container
        html.Div([
            # Left panel - Controls
            html.Div([
                # Date picker section
                html.Div([
                    html.Label('Rango de Fechas:', 
                              style={
                                  'fontWeight': '600',
                                  'marginBottom': '0.5rem',
                                  'display': 'block',
                                  'color': COLORS['text'],
                                  'fontFamily': 'Inter, sans-serif'
                              }),
                    dcc.DatePickerRange(
                        id='date-picker',
                        min_date_allowed=df['FECHA'].min(),
                        max_date_allowed=df['FECHA'].max(),
                        start_date=df['FECHA'].max() - timedelta(days=30),
                        end_date=df['FECHA'].max(),
                        display_format='YYYY-MM-DD',
                        style={
                            'zIndex': 10,
                            'background': COLORS['background']
                        },
                        calendar_orientation='horizontal',
                        updatemode='bothdates',
                        clearable=True,
                        day_size=35,
                        with_portal=True,
                        first_day_of_week=1,
                        month_format='MMMM YYYY',
                        number_of_months_shown=2,
                        persistence=True,
                        persisted_props=['start_date', 'end_date'],
                        persistence_type='session',
                        start_date_placeholder_text='Fecha inicial',
                        end_date_placeholder_text='Fecha final',
                        minimum_nights=0,
                        stay_open_on_select=False,
                        show_outside_days=True,
                        initial_visible_month=df['FECHA'].max(),
                        className='date-picker-custom',
                    )
                ], style={
                    'marginBottom': '2rem',
                    'padding': '1rem',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                }),
                
                # Technical indicators section
                html.Div([
                    html.Label('Indicadores Técnicos:', 
                              style={
                                  'fontWeight': '600',
                                  'marginBottom': '1rem',
                                  'display': 'block',
                                  'color': COLORS['text'],
                                  'fontFamily': 'Inter, sans-serif'
                              }),
                    dcc.Checklist(
                        id='indicators-checklist',
                        options=[
                            {'label': ' Bandas de Bollinger', 'value': 'bb'},
                            {'label': ' Media Móvil 7 días', 'value': 'sma_weekly'},
                            {'label': ' Media Móvil 30 días', 'value': 'sma_monthly'},
                            {'label': ' Diferencial Pico/Valle', 'value': 'peak_spread'}
                        ],
                        value=[],
                        style={'color': COLORS['text']},
                        inputStyle={
                            "marginRight": "0.5rem",
                            "cursor": "pointer"
                        },
                        labelStyle={
                            'display': 'block',
                            'marginBottom': '1rem',
                            'padding': '0.5rem',
                            'borderRadius': '8px',
                            'transition': 'background-color 0.2s',
                            'cursor': 'pointer',
                            'fontFamily': 'Inter, sans-serif'
                        }
                    )
                ], style={
                    'padding': '1rem',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], style={'width': '300px', 'marginRight': '2rem'}),
            
            # Right panel - Chart and Stats
            html.Div([
                # Stats panel
                html.Div([
                    html.Div(id='price-stats', style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'gap': '1rem',
                        'marginBottom': '1rem',
                        'fontFamily': 'Inter, sans-serif',
                        'flexWrap': 'wrap'
                    })
                ], style={
                    'padding': '1.5rem',
                    'backgroundColor': COLORS['background'],
                    'borderRadius': '12px',
                    'marginBottom': '1rem'
                }),
                
                # Chart
                html.Div([
                    dcc.Graph(
                        id='price-chart',
                        config={
                            'displayModeBar': True,
                            'scrollZoom': True,
                            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': 'precio_electricidad',
                                'height': 800,
                                'width': 1200,
                                'scale': 2
                            }
                        }
                    )
                ], style={
                    'padding': '1rem',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
                })
            ], style={'flex': 1})
        ], style={
            'display': 'flex',
            'marginBottom': '2rem'
        })
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'padding': '2rem'
    })
])

### METHODS --> CALLBACKS ###
# Add callback for price stats
@app.callback(
    Output('price-stats', 'children'), #output = price stats displayed on the cards 
    [Input('date-picker', 'start_date'), #input = start and end date of the selected timeframe
     Input('date-picker', 'end_date')] 
)
def update_stats(start_date, end_date):
    # Handle case when dates are cleared
    if start_date is None or end_date is None:
        #display the entire date range of data  available
        start_date = df['FECHA'].min()
        end_date = df['FECHA'].max()
    
    mask = (df['FECHA'] >= start_date) & (df['FECHA'] <= end_date)
    filtered_df = df[mask]
    
    stats = [
        {'name': 'Mínimo', 'value': filtered_df['PRECIO'].min()},
        {'name': 'Máximo', 'value': filtered_df['PRECIO'].max()},
        {'name': 'Promedio', 'value': filtered_df['PRECIO'].mean()},
        {'name': 'Desviación', 'value': filtered_df['PRECIO'].std()}
    ]
    
    return [
        html.Div([
            html.Div(stat['name'], 
                    style={
                        'color': COLORS['primary'],
                        'fontSize': '1.1rem',
                        'fontWeight': '500',
                        'textAlign': 'center',
                        'marginBottom': '0.5rem'
                    }),
            html.Div(f"{stat['value']:.2f} €/MWh", 
                    style={
                        'color': COLORS['text'],
                        'fontSize': '1.3rem',
                        'fontWeight': '600',
                        'textAlign': 'center'
                    })
        ], style={
            'padding': '1rem',
            'borderRadius': '12px',
            'backgroundColor': 'white',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
            'flex': '1',
            'margin': '0 0.5rem',
            'minWidth': '180px'
        }) for stat in stats
    ]

# Add callback for price chart
@app.callback(
    Output('price-chart', 'figure'), #output the figure to be displayed
    [Input('date-picker', 'start_date'), #input = start and end date of the selected timeframe
     Input('date-picker', 'end_date'),
     Input('indicators-checklist', 'value')] #input = the indicators selected
)
def update_chart(start_date, end_date, indicators):
    # Handle case when dates are cleared
    if start_date is None or end_date is None:
        start_date = df['FECHA'].min()
        end_date = df['FECHA'].max()
    
    mask = (df['FECHA'] >= start_date) & (df['FECHA'] <= end_date)
    filtered_df = df[mask].copy()
    
    # Create the figure with two rows if peak/spread is selected
    if 'peak_spread' in indicators:
        fig = make_subplots(rows=2, cols=1, 
                           row_heights=[0.7, 0.3],
                           shared_xaxes=True, 
                           vertical_spacing=0.05)
    else:
        fig = make_subplots(rows=1, cols=1)
    
    # Add price line with gradient fill
    fig.add_trace(
        go.Scatter(
            x=filtered_df['DATETIME'], 
            y=filtered_df['PRECIO'],
            name='Precio', 
            line=dict(color=COLORS['primary'], width=2, shape='spline'),
            fill='tonexty',
            fillcolor=f'rgba({int(COLORS["primary"][1:3], 16)}, {int(COLORS["primary"][3:5], 16)}, {int(COLORS["primary"][5:7], 16)}, 0.1)',
            hovertemplate='<b>Precio:</b> %{y:.2f} €/MWh<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add selected indicators
    if indicators:
        if 'bb' in indicators:
            upper, middle, lower = calculate_bollinger_bands(filtered_df['PRECIO'])
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=upper,
                          name='BB Superior', line=dict(color='red', dash='dash')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=middle,
                          name='BB Media', line=dict(color='red')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=lower,
                          name='BB Inferior', line=dict(color='red', dash='dash')),
                row=1, col=1
            )
        
        if 'sma_weekly' in indicators:
            sma_short = calculate_sma(filtered_df['PRECIO'], 24*7)  # 7-day SMA
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=sma_short,
                          name='Media 7 días', line=dict(color='#FFA500')),
                row=1, col=1
            )
        
        if 'sma_monthly' in indicators:
            sma_long = calculate_sma(filtered_df['PRECIO'], 24*30)  # 30-day SMA
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=sma_long,
                          name='Media 30 días', line=dict(color='magenta')),
                row=1, col=1
            )
        
        if 'peak_spread' in indicators:
            spread = calculate_peak_offpeak_spread(filtered_df) #configure the peak hours in the function   
            fig.add_trace(
                go.Scatter(x=filtered_df['DATETIME'], y=spread,
                          name='Diferencial Pico/Valle',
                          line=dict(color='blue'),
                          hovertemplate='<b>Diferencial:</b> %{y:.2f} €/MWh<extra></extra>'),
                row=2, col=1
            )
            fig.update_yaxes(title_text="Diferencial Pico/Valle (€/MWh)", row=2, col=1)
    
    # Update layout with improved styling
    fig.update_layout(
        title=None,
        xaxis_title='Fecha',
        yaxis_title='Precio (€/MWh)',
        height=800 if 'peak_spread' in indicators else 600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(family="Inter, sans-serif")
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=30, b=50),
        font=dict(family="Inter, sans-serif")
    )
    
    # Update axes styling
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['grid'],
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor=COLORS['grid']
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor=COLORS['grid'],
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor=COLORS['grid'],
        side='right'  # Add price scale on right side
    )
    
    return fig

# Add callback for timeframe buttons
@app.callback(
    [Output('date-picker', 'start_date'), #output the start and end date of the selected timeframe
     Output('date-picker', 'end_date')],
    [Input('1d-button', 'n_clicks'), #input = clicks of the time frame buttons
     Input('1w-button', 'n_clicks'),
     Input('1m-button', 'n_clicks'),
     Input('3m-button', 'n_clicks'),
     Input('6m-button', 'n_clicks'),
     Input('1y-button', 'n_clicks'),
     Input('max-button', 'n_clicks')]
)
def update_timeframe(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    end_date = df['FECHA'].max()
    
    timeframes = {
        '1d-button': timedelta(days=1),
        '1w-button': timedelta(days=7),
        '1m-button': timedelta(days=30),
        '3m-button': timedelta(days=90),
        '6m-button': timedelta(days=180),
        '1y-button': timedelta(days=365),
        'max-button': end_date - df['FECHA'].min()
    }
    
    if button_id in timeframes:
        start_date = end_date - timeframes[button_id]
        return start_date, end_date
    
    return dash.no_update, dash.no_update

# Add custom CSS to the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .date-picker-custom .SingleDatePickerInput,
            .date-picker-custom .DateRangePickerInput {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            
            .date-picker-custom .DateInput_input {
                font-family: 'Inter', sans-serif;
                font-size: 0.9rem;
                border-radius: 8px;
                color: #1e293b;
                padding: 8px 12px;
            }
            
            .date-picker-custom .DateInput_input__focused {
                border-color: #4AD7D4;
            }
            
            .date-picker-custom .CalendarDay__selected,
            .date-picker-custom .CalendarDay__selected:hover {
                background: #4AD7D4;
                border: 1px solid #4AD7D4;
                color: white;
            }
            
            .date-picker-custom .CalendarDay__selected_span {
                background: rgba(74, 215, 212, 0.1);
                border: 1px solid rgba(74, 215, 212, 0.2);
                color: #00B2AF;
            }
            
            .date-picker-custom .CalendarDay__hovered_span,
            .date-picker-custom .CalendarDay__hovered_span:hover {
                background: rgba(74, 215, 212, 0.1);
                border: 1px solid rgba(74, 215, 212, 0.2);
                color: #00B2AF;
            }
            
            .date-picker-custom .DayPickerKeyboardShortcuts_show__bottomRight::before {
                border-right-color: #4AD7D4;
            }
            
            .date-picker-custom .CalendarDay__today {
                border: 1px solid #4AD7D4;
                color: #00B2AF;
            }
            
            .timeframe-button {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Inter', sans-serif;
                font-size: 0.9rem;
                color: #1e293b;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .timeframe-button:hover {
                background-color: rgba(74, 215, 212, 0.1);
                border-color: #4AD7D4;
                color: #00B2AF;
            }
            
            .timeframe-button:active {
                background-color: #4AD7D4;
                color: white;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True) 