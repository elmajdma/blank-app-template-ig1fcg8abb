import streamlit as st
import pandas as pd
from io import StringIO
import lasio
import numpy as np
from tempfile import NamedTemporaryFile
import matplotlib.pyplot as plt
import altair as alt

feature_target = ['DT', 'GR', 'NPHI', 'PEF', 'RHOB']

st.set_page_config(page_title='Log Assitant',
                   page_icon='./icons8-rig-64.png',
                   layout="wide")

st.title('log Assitant\u00A9')
st.text('Predict Missing log data, Easy and Straight Forward !!')
st.text('Mohammed Abu El Majd, 2024\u00A9')
st.divider()
st.write('Happy to conact me (elmajdma@gmail.com)')
st.markdown('Note: this version 1 of web application')
st.sidebar.image('./Multi-layer-map_1.png', use_column_width=True)

st.subheader(f'Upload Data File', divider='rainbow')
mode = st.radio(
    "Select an option:",
    ('None', 'Upload LAS File', 'Upload CSV File'), index=0 )
# Handle the selection
if mode == 'None':
    st.write("No option selected")

elif mode == 'Upload LAS File':
    file = st.file_uploader('Upload the LAS file')
    if file is not None:
        tfile = NamedTemporaryFile(delete=False)
        tfile.write(file.read())
        las_file = lasio.read(tfile.name)
        las_df = las_file.df()
        las_df.insert(0, 'DEPTH', las_df.index)
        las_df.reset_index(drop=True, inplace=True)
        
    
        try:
            well_name = las_file.header['Well'].WELL.value
            uwi = las_file.header['Well'].UWI.value
            start_depth = las_df['DEPTH'].min()
            stop_depth = las_df['DEPTH'].max()
            step = abs(las_file.header['Well'].STEP.value)
            company_name = las_file.header['Well'].COMP.value
            date = las_file.header['Well'].DATE.value
            curvename = las_file.curves

        except:
            well_name = 'unknown'
            uwi = 'unknown'
            start_depth = 0.00
            stop_depth = 10000.00
            step = abs(las_df['DEPT'][1]-las_df['DEPT'][0])
            company_name = 'unknown'
            date = 'unknown'
            curvename = las_file.curves

    st.subheader(f'Well Information', divider='rainbow')
    st.text(f'Well Name : {well_name}')
    st.text(f'UWI: {uwi}')
    st.text(f'Start Depth : {start_depth}')
    st.text(f'Stop Depth : {stop_depth}')
    st.text(f'Step : {step}')
    st.text(f'Company : {company_name}')
    st.text(f'Logging Date : {date}')    


elif mode == 'Upload CSV File':
    file = st.file_uploader('Upload CSV file')
    if file is not None:
        tfile = NamedTemporaryFile(delete=False)
        tfile.write(file.read())
        las_df = pd.read_csv(tfile.name)
        las_df.insert(0, 'DEPTH', las_df.index)
        las_df.reset_index(drop=True, inplace=True)

st.divider()
st.subheader(f'Select Prediction Model', divider='rainbow')
model_selection = st.radio('', options=(
    'Sonic Log Prediction', 'Litho-Facies Prediction'))

if model_selection == 'Sonic Log Prediction':
    pass

if model_selection == 'Litho-Facies Prediction':
    pass

st.subheader(f'Selecting Well logs', divider='rainbow')
curves = las_df.columns.values

if 'GR' in curves:
    gr_col = las_df.columns.get_loc('GR')
else:
    gr_col = 0

if 'PEF' in curves:
    pef_col = las_df.columns.get_loc('PEF')
else:
    pef_col = 0

if 'RHOB' in curves:
    den_col = las_df.columns.get_loc('RHOB')
else:
    den_col = 0

if 'NPHI' in curves:
    neu_col = las_df.columns.get_loc('NPHI')
else:
    neu_col = 0

gr_curve = st.selectbox('select the GAMMA RAY curve', curves, index=gr_col)
pef_curve = st.selectbox(
    'select the Photoelectric Factor curve', curves, index=pef_col)
den_curve = st.selectbox(
    'select the BULK DENSITY curve', curves, index=den_col)
neu_curve = st.selectbox(
    'select the NEUTRON POROSITY curve', curves, index=neu_col)
curve_list = [gr_curve, pef_curve, den_curve, neu_curve,]
# curve_list=['GR','PEF','RHOB' 'NPHI' ]


st.sidebar.title('Plot Setting')
well_name = st.sidebar.text_input('Well Name', value=(well_name))
well_df = las_df.copy()

top_depth = st.sidebar.number_input(
    'Top Depth', min_value=0.00, value=(start_depth), step=100.00)
bot_depth = st.sidebar.number_input(
    'Base Depth', min_value=0.00, value=(stop_depth), step=100.00)
st.sidebar.divider()

interval = alt.selection_interval()

# Base chart with interval selection
base = alt.Chart(las_df).mark_line(point=False).encode(
    alt.Y('DEPTH:Q',  scale=alt.Scale(domain=[bot_depth, top_depth])),
    # order = 'DEPTH',
).properties(
    width=250,
    height=2000,

).add_params(interval)

base2 = alt.Chart(las_df).mark_line(point=False).encode(
    alt.Y('DEPTH:Q', scale=alt.Scale(domain=[bot_depth, top_depth]),
          axis=alt.Axis(labels=False), title=''),


).properties(
    width=250,
    height=2000,
    title='',

).add_params(interval)

# GR chart
gr = base.mark_line(interpolate='monotone', color='green', clip=True).encode(
    # x='GR:Q',
    alt.X('GR:Q', scale=alt.Scale(domain=[0, 200]), axis=alt.Axis(
        labelAngle=0, title='GR', orient='top')),
    order='DEPTH', tooltip='GR:Q',


).properties().add_params(interval)

# RHOB chart
rhob = base2.mark_line(interpolate='monotone', color='red', clip=True).encode(
    alt.X('RHOB:Q', scale=alt.Scale(domain=[1.9, 3]), axis=alt.Axis(title='RHOB', orient='top')), color=alt.value('red'),
    order='DEPTH',
).properties(


).add_params(interval)

# NPHI chart
nphi = base2.mark_line(interpolate='monotone', color='yellow', clip=True).encode(
    alt.X('NPHI:Q', scale=alt.Scale(
        domain=[0.44, -0.2]), axis=alt.Axis(title='NPHI', orient='top', titleY=-30)),
    color=alt.value('yellow'),
    order='DEPTH',
).properties(

).add_params(interval)

pef = base2.mark_line(interpolate='monotone', color='brown', clip=True).encode(
    alt.X('PEF:Q', scale=alt.Scale(domain=[1, 15]), axis=alt.Axis(
        labelAngle=0, title='PEF', orient='top')),
    color=alt.value('brown'),
    order='DEPTH',
).properties(

).add_params(interval)

chart_nphi_rhob = alt.layer(rhob, nphi).resolve_scale(
    x='independent',
).properties(

).add_params(interval)

labels = alt.Chart(las_df).mark_text(
    align='center',
    baseline='bottom'
).encode(
    x=alt.value(0),  # Position the text manually
    y=alt.value(-40),  # Adjust the vertical position as needed
    text=alt.Text('RHOB:Q')
).transform_calculate(
    text='"RHOB"'
)

com_chart = chart_nphi_rhob | labels
# Combine the charts
combined_chart = gr | com_chart | pef

combined_chart.configure_header(

    titleColor='white',
    titleFontSize=16,
    labelColor='red',
    labelFontSize=14,

)

# Streamlit app layout
st.title("Well Log Data Visualization")
st.altair_chart(combined_chart, use_container_width=True)  # ,
