import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load your Excel data
data_path = '/Users/margarita/Desktop/Scorecards_final.xlsx'
df = pd.read_excel(data_path)

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define custom CSS styles for the dropdown
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom Dropdown */
            .customDropdown {
                font-size: 16px;
                font-family: "Poppins";
                padding-left: 1px;
            }

            .customDropdown .Select-control {
                width: 100%;
                height: 38px;
                background-color: transparent;
                border: 1px solid #676768;
                border-radius: 3px;
                color: var(--bs-info) !important;
            }

            .customDropdown .Select-value-label,
            .customDropdown .Select-placeholder {    
                color: var(--bs-info) !important;
            }

            .customDropdown .Select-arrow {
                border-color: #cccccc transparent transparent;
            }

            .customDropdown.is-open .Select-arrow {
                border-color: transparent transparent #cccccc;
            }

            .customDropdown .Select-clear {
                color: var(--bs-info);
                font-size: 22px;
            }

            .customDropdown.is-focused:not(.is-open) > .Select-control {
                border: 2px solid color-mix(in srgb, var(--bs-info), #010103 50%) !important;
            }

            .customDropdown.is-focused:not(.is-open) .Select-arrow {
                border-color: var(--bs-info) transparent transparent;
            }

            .customDropdown .Select-menu-outer {
                margin-top: 5px;
                border-radius: 3px;
                background-color: #010103;
                border: 1px solid #676768;
                color: var(--bs-light);
            }

            .customDropdown .VirtualizedSelectFocusedOption {
                background-color: color-mix(in srgb, var(--bs-light), #010103 7%);
                border-radius: 3px;
                color: #010103;
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

# Layout for the Overview page
overview_layout = html.Div([
    html.H1('Overview'),
    dcc.Dropdown(
        id='scorecard-dropdown',
        className='customDropdown',
        options=[{'label': name, 'value': name} for name in df['Scorecard name'].unique()],
        placeholder="Select a Scorecard",
    ),
    dcc.Graph(id='bar-chart'),
    html.Hr(),
    html.H3('Details'),
    html.Div(id='table-container')
])

# Layout for the Details page
details_layout = html.Div([
    html.H1('Details Page'),
    # Additional content for the details page (if needed)
])

# Main layout including navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/details':
        return details_layout
    else:
        return overview_layout

# Update the bar chart based on dropdown selection
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('scorecard-dropdown', 'value')]
)
def update_bar_chart(scorecard_name):
    if scorecard_name:
        filtered_df = df[df['Scorecard name'] == scorecard_name]
    else:
        filtered_df = df

    fig = px.bar(filtered_df, x='IMS year', y='IMS status', color='IMS status', barmode='group', custom_data=['IMS status'])
    fig.update_layout(title=f"Number of IMS Status per Year for {scorecard_name or 'All Scorecards'}")
    return fig

# Update the table based on bar chart selection
@app.callback(
    Output('table-container', 'children'),
    [Input('bar-chart', 'clickData')]
)
def update_table(click_data):
    if click_data:
        selected_year = click_data['points'][0]['x']
        selected_status = click_data['points'][0]['customdata'][0] if 'customdata' in click_data['points'][0] else None

        filtered_df = df[
            (df['IMS year'] == selected_year) &
            (df['IMS status'] == selected_status)
        ]

        if filtered_df.empty:
            return html.Div("No matching data found.", style={"color": "red"})

        return dbc.Table.from_dataframe(filtered_df, striped=True, bordered=True, hover=True)
    else:
        return html.Div("Please select a point on the chart to see the details.")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
