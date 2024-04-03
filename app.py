# %%
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go # or plotly.express as px
from plotly.express import data
import statsmodels

# %%
# Import data
df = pd.read_csv('actualdata.csv')
df.head()

# %%
# Convert Date column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Extract month from Date column
df['Month'] = df['Date'].dt.month_name()

# Initialize the Dash app
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # Load the CSS stylesheet
app = dash.Dash(__name__, external_stylesheets=stylesheets)  # Initialize the app
server = app.server


# Define scatter plot function
def scatter_plot(selected_month, uncolored_dots, n_clicks, trendline_on):
    filtered_df = df[df['Month'] == selected_month]

    if 'include' not in uncolored_dots:  # Check if the "Include" checkbox is not checked
        # Filter out rows with missing BMI values and drop rows where BMIBin is 'Unknown'
        filtered_df = filtered_df.dropna(subset=['BMIBin'])
        filtered_df = filtered_df[filtered_df['BMIBin'] != 'Unknown']

    # Define color mapping and legend labels
    color_map = {'Normal': 'purple', 'Overweight': 'red', 'Unknown': 'lightblue'}
    legend_labels = {'Normal': 'Normal BMI', 'Overweight': 'Overweight BMI', 'Unknown': 'Unknown BMI'}

    # Determine variables for x and y axes
    if n_clicks % 2 == 0:
        x_axis, y_axis = 'StepTotal', 'Calories'
    else:
        x_axis, y_axis = 'Calories', 'StepTotal'

    scatter_fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color='BMIBin', hover_name='Id',
                             title=f"{x_axis} vs {y_axis} with BMI color scale ({selected_month})",
                             color_discrete_map=color_map, labels={'BMIBin': 'BMI'},
                             trendline="ols" if trendline_on else None)  # Apply color mapping and legend labels

    scatter_fig.update_traces(marker=dict(size=10))

    scatter_fig.update_layout(margin=dict(
        l=50,
        r=170,
        b=100,
        t=100,
        pad=4
    ),
        paper_bgcolor="white", )

    return scatter_fig


# Define app layout
app.layout = html.Div([
    # Left column: Heading
    html.Div([
        html.H1("Fitness Activity Dashboard", className="header-title"),
        html.Div(
            "This dashboard is for physical therapists with 30 patients with health data spanning from April 12 to March 12. It gives an overview of how various health attributes affect the others, and of the patterns amongst and within users as well. This can also be used by public health organizations to monitor population-level trends, develop targeted interventions, and advocate for policies that support healthier lifestyles.",
            className="header-description")  # Description text
    ], className="four columns"),

    # Right column: Scatter plot and controls
    html.Div([
        # Wrapper for the scatter plot and controls
        html.Div([
            # Scatter plot
            html.Div([
                dcc.Graph(id='scatter-plot', style={'padding-right': '50px', 'padding-bottom': '50px'}),
            ], style={'position': 'relative'}),

            # Controls (bottom right corner)
            html.Div([
                html.Div([
                    html.Label("Customization:", className="control-label"),
                    # Radio button for month selection
                    dcc.RadioItems(
                        id='month-radio',
                        options=[{'label': month, 'value': month} for month in ['April', 'May']],
                        value='April',  # Default selection
                        labelStyle={'display': 'block'},
                        className="control-radio"
                    ),
                    # Switch Axes button
                    html.Button("Switch Axes", id='switch-axes-button', n_clicks=0, className="control-button"),
                    # Include checkbox
                    dcc.Checklist(
                        id='uncolored-dots-checkbox',
                        options=[{'label': 'Users without BMI', 'value': 'include'}],
                        value=[],
                        className="control-checkbox"
                    ),
                    # Trendline checkbox
                    dcc.Checklist(
                        id='trendline-checkbox',
                        options=[{'label': 'Show Trendlines', 'value': 'trendline_on'}],
                        value=['trendline_on'],
                        className="control-checkbox"
                    ),
                ], className="controls-box"),
            ], style={'position': 'absolute', 'bottom': 150, 'right': 50, 'padding': '5px',
                      'background-color': 'white', 'border': '1px solid grey', 'border-radius': '5px'}),

        ], className="eight columns", style={'padding-top': '40px', 'position': 'relative'}),  # Adjust padding-top
    ], className="eight columns")
], className="row")


# Define callback to update scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('month-radio', 'value'),
     Input('uncolored-dots-checkbox', 'value'),
     Input('switch-axes-button', 'n_clicks'),
     Input('trendline-checkbox', 'value')]
)
def update_scatter_plot_callback(selected_month, uncolored_dots, n_clicks, trendline_on):
    return scatter_plot(selected_month, uncolored_dots, n_clicks, 'trendline_on' in trendline_on)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


