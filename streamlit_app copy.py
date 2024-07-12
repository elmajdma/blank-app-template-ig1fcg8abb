import streamlit as st
import pandas as pd
from io import StringIO
import lasio
import numpy as np
from tempfile import NamedTemporaryFile
import matplotlib.pyplot as plt
import altair as alt
from pandas_profiling import ProfileReport
import streamlit.components.v1 as components
import joblib

feature_target = ['GR', 'NPHI', 'PEF', 'RHOB']
loaded_model = joblib.load('./sonic_prediction_model.pkl')

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

def create_base_chart(data, bot_depth, top_depth):
    """
    Create a base chart with interval selection.
    """
    interval = alt.selection_interval()

    base = alt.Chart(data).mark_line(point=False).encode(
        alt.Y('DEPTH:Q', scale=alt.Scale(domain=[bot_depth, top_depth])),
    ).properties(
        width=250,
        height=2000,
    ).add_params(interval)

    return base, interval

def create_base2_chart(data, bot_depth, top_depth):
    """
    Create a base chart with interval selection.
    """
    interval = alt.selection_interval()

    base = alt.Chart(data).mark_line(point=False).encode(
        alt.Y('DEPTH:Q', scale=alt.Scale(domain=[bot_depth, top_depth]),
              axis=alt.Axis(labels=False), title='')).properties(
        width=250,
        height=2000,
    ).add_params(interval)

    return base, interval


def create_gr_chart(base, interval):
    """
    Create the GR chart.
    """
    gr = base.mark_line(interpolate='monotone', color='green', clip=True).encode(
        alt.X('GR:Q', scale=alt.Scale(domain=[0, 200]), axis=alt.Axis(
            labelAngle=0, title='GR', orient='top')),
        order='DEPTH',
        tooltip='GR:Q',
    ).properties().add_params(interval)

    return gr

def create_rhob_chart(base2, interval):
    """
    Create the RHOB chart.
    """
    rhob = base2.mark_line(interpolate='monotone', color='red', clip=True).encode(
        alt.X('RHOB:Q', scale=alt.Scale(domain=[1.9, 3]), axis=alt.Axis(title='RHOB', orient='top')),
        color=alt.value('red'),
        order='DEPTH',
    ).properties().add_params(interval)

    return rhob

def create_nphi_chart(base2, interval):
    """
    Create the NPHI chart.
    """
    nphi = base2.mark_line(interpolate='monotone', color='yellow', clip=True).encode(
        alt.X('NPHI:Q', scale=alt.Scale(domain=[0.44, -0.2]), axis=alt.Axis(title='NPHI', orient='top', titleY=-30)),
        color=alt.value('yellow'),
        order='DEPTH',
    ).properties().add_params(interval)

    return nphi

def create_pef_chart(base2, interval):
    """
    Create the PEF chart.
    """
    pef = base2.mark_line(interpolate='monotone', color='brown', clip=True).encode(
        alt.X('PEF:Q', scale=alt.Scale(domain=[1, 15]), axis=alt.Axis(labelAngle=0, title='PEF', orient='top')),
        color=alt.value('brown'),
        order='DEPTH',
    ).properties().add_params(interval)

    return pef
def create_dt_chart(base2, interval):
    """
    Create the dt chart.
    """
    pef = base2.mark_line(interpolate='monotone', color='yellow', clip=True).encode(
        alt.X('DT_predcited:Q', scale=alt.Scale(domain=[140, 40]), axis=alt.Axis(labelAngle=0, title='DT Predicted', orient='top')),
        color=alt.value('yellow'),
        order='DEPTH',
    ).properties().add_params(interval)

    return pef
def create_labels_chart(data):
    """
    Create labels for the RHOB chart.
    """
    labels = alt.Chart(data).mark_text(
        align='center',
        baseline='bottom'
    ).encode(
        x=alt.value(0),  # Position the text manually
        y=alt.value(-40),  # Adjust the vertical position as needed
        text=alt.Text('RHOB:Q')
    ).transform_calculate(
        text='"RHOB"'
    )

    return labels

def create_combined_char_dt(gr, chart_nphi_rhob, pef, dt):
    """
    Combine all charts into one.
    """
    combined_chart = gr | chart_nphi_rhob | pef |dt

    combined_chart = combined_chart.configure_header(
        titleColor='white',
        titleFontSize=16,
        labelColor='red',
        labelFontSize=14,
    )

    return combined_chart

def create_combined_chart(gr, chart_nphi_rhob, pef):
    """
    Combine all charts into one.
    """
    combined_chart = gr | chart_nphi_rhob | pef 

    combined_chart = combined_chart.configure_header(
        titleColor='white',
        titleFontSize=16,
        labelColor='red',
        labelFontSize=14,
    )

    return combined_chart
# Create base charts
base, interval = create_base_chart(las_df, bot_depth, top_depth)
base2, _ = create_base2_chart(las_df, bot_depth, top_depth)

# Create individual charts
gr = create_gr_chart(base, interval)
rhob = create_rhob_chart(base2, interval)
nphi = create_nphi_chart(base2, interval)
pef = create_pef_chart(base2, interval)
labels = create_labels_chart(las_df)

# Combine charts
chart_nphi_rhob = alt.layer(rhob, nphi).resolve_scale(
    x='independent',
).properties().add_params(interval)

com_chart = chart_nphi_rhob | labels
combined_chart = create_combined_chart(gr, com_chart, pef)

# Streamlit app layout
st.title("Well Log Data Visualization")
st.altair_chart(combined_chart, use_container_width=True)



#if st.header("Statistical Analysis Report")
 #   profile = ProfileReport(las_df, title="Statistical Analysis Report", explorative=True)
  #  profile_html = profile.to_html()
   # components.html(profile_html, height=800, scrolling=True)

# Add a button to perform an additional action
if st.sidebar.button('Data Summary'):
    st.header("Data Summary")
    st.write(las_df.describe())
st.divider()   
st.subheader(f'Model Prediction', divider='rainbow')
las_nan=las_df.copy()
las_nan.dropna(axis=0, inplace=True)
prediction = loaded_model.predict(las_nan[feature_target])
las_nan['DT_predcited']=prediction
st.write(prediction)


# Create base charts
base, interval = create_base_chart(las_nan, bot_depth, top_depth)
base2, _ = create_base2_chart(las_nan, bot_depth, top_depth)

# Create individual charts
gr = create_gr_chart(base, interval)
rhob = create_rhob_chart(base2, interval)
nphi = create_nphi_chart(base2, interval)
pef = create_pef_chart(base2, interval)
dt=create_dt_chart(base2, interval)
labels = create_labels_chart(las_nan)

# Combine charts
chart_nphi_rhob = alt.layer(rhob, nphi).resolve_scale(
    x='independent',
).properties().add_params(interval)

com_chart = chart_nphi_rhob | labels
combined_chart = create_combined_char_dt(gr, com_chart, pef, dt)
# Streamlit app layout
st.title("Well Log Data Visualization")
st.altair_chart(combined_chart, use_container_width=True)
    
# load the model from disk
