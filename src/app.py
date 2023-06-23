import plotly.express as px
import streamlit as st
import pandas as pd
from datetime import datetime as dt
import matplotlib
import matplotlib.pyplot as plt



def color_metric_background(metric_value, color_map, metric_min = 0,metric_max=1 ):
    # Define the colormap
    cmap = plt.get_cmap(color_map)

    # Normalize the metric value to the range [0, 1]
    normalized_value = (metric_value - metric_min) / (metric_max - metric_min)

    # Map the normalized value to the colormap range [0, 256]
    cmap_value = int(normalized_value * 255)

    # Get the RGB color tuple from the colormap
    color = cmap(cmap_value)[:3]

    # Convert RGB color to hexadecimal
    hex_color = '#%02x%02x%02x' % tuple([int(x * 255) for x in color])

    # Create CSS style for the colored background
    background_style = f'background-color: {hex_color};'

    return background_style

def make_plots(df, y_bar,y_line, x) :
    fig = px.bar(
        df,
        x=resolution,
        y=y_bar,
    )
    fig_available = px.line(
        df,
        x=resolution,
        y=y_line,
        labels=y_line, color_discrete_sequence=['red']
    )

    fig.add_traces(
    list(fig_available.select_traces())

    )

    name = ['avg used','available']

    for i in range(len(fig.data)):
        fig.data[i]['name'] = name[i]
        fig.data[i]['showlegend'] = True
    return fig

def get_kpi_metrics(df, metrics):
    kpi = []
    for metric in metrics:
        kpi_col = f'kpi_{metric}'
        usage_col = f'usage_{metric}'
        available_col =f'available_{metric}'
        df[kpi_col] = round(100*df[usage_col]/df[available_col],1)
        kpi.append(kpi_col)
    return df, kpi


# Load data
df_metrics = pd.read_csv("data/input_data.csv")
df_metrics["month"] = pd.PeriodIndex(df_metrics.week, freq="M")
df_metrics["quarter"] = pd.PeriodIndex(df_metrics.week, freq="Q")

# Inputs
metrics= ['A','B']
COLOR_MAP = 'RdYlGn'


# Calculate avg metrics by month
df_metrics_month = (
    df_metrics.groupby(["month", "quarter"])
    .agg(
        usage_A=("usage_A", "mean"),
        usage_B=("usage_B", "mean"),
        available_A =("available_A", "mean"),
        available_B=("available_B", "mean"),
    )
    .reset_index()
)

# Calculate avg metrics by quarter
df_metrics_quarter = (
    df_metrics.groupby(["quarter"])
    .agg(
        usage_A=("usage_A", "mean"),
        usage_B=("usage_B", "mean"),
        available_A =("available_A", "mean"),
        available_B=("available_B", "mean"),
    )
    .reset_index()
)

# Store all resolutions in a dictionary
## Having the information pre-aggregated facilitates the speed of the application
resolutions = ["week","month", "quarter"]
metric_frames = {"week":df_metrics,"month": df_metrics_month, "quarter": df_metrics_quarter}

# Calculate KPI metrics by week, quarter and month for all metrics in list
df_metrics, kpi_metrics  = get_kpi_metrics(df_metrics, metrics)
df_metrics_month, kpi_metrics  = get_kpi_metrics(df_metrics_month, metrics)
df_metrics_quarter, kpi_metrics = get_kpi_metrics(df_metrics_quarter, metrics)

# Create a table to display in the dashboard.
## The table is transposed to ease reading
kpi_frames = {"week" : df_metrics[['week'] + kpi_metrics].set_index('week').T,
              "month": df_metrics_month[['month'] + kpi_metrics].set_index('month').T,
              "quarter": df_metrics_quarter[['quarter'] + kpi_metrics].set_index('quarter').T}


st.set_page_config(layout="wide")
col1, col2 = st.columns(2)
col1.title("KPI usage Dashboard")
col2.markdown("[Link to repo](https://github.com/alexane-rose/streamlit-app)")

# Current Month metrics
cols = st.columns(len(metrics))
current_month = pd.Period(dt.today(),freq='M')
current_month_metrics = df_metrics_month.loc[df_metrics_month.month == current_month ].reset_index(drop=True)

i=0

for col in cols:
   kpi_col = f'kpi_{metrics[i]}'
   col.markdown(f'<h1 style="{color_metric_background(current_month_metrics[kpi_col][0], COLOR_MAP,0,100)}"><center>{current_month_metrics[kpi_col][0]}%</center></h1>', unsafe_allow_html=True)
   i+=1

resolution = st.radio("Time resolution", resolutions)

# KPI table
st.table(kpi_frames[resolution].style.background_gradient(cmap=COLOR_MAP, vmin= 0 , vmax=100).format("{:.1f}%"))

# Bar charts
df_metrics_quarter['quarter'] = df_metrics_quarter['quarter'].astype('str')
df_metrics_month['month'] = df_metrics_month['month'].astype('str')

figs = []
for metric in metrics:
    usage_col = f'usage_{metric}'
    available_col = f'available_{metric}'
    fig = make_plots(metric_frames[resolution],usage_col,available_col,resolution)
    figs.append(fig)

cols = st.columns(len(metrics))
i=0
for col in cols:
    col.markdown(f'### Avg Usage vs Availble of {metrics[i]} over time')
    col.plotly_chart(figs[i],  theme="streamlit", use_container_width=True)
    i+=1
