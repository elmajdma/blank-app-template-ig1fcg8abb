import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
import joblib
import utils.log_utils as log_utils  # Import the module

feature_target = ['GR', 'NPHI', 'PEF', 'RHOB']
loaded_model = joblib.load('./sonic_prediction_model.pkl')

st.set_page_config(page_title='Log Assistant',
                   page_icon='./icons8-rig-64.png',
                   layout="wide")

st.title('Log Assistant\u00A9')
st.text('Predict Missing log data, Easy and Straight Forward !!')
st.text('Mohammed Abu El Majd, 2024\u00A9')
st.write('Happy to contact me (elmajdma@gmail.com)')
st.markdown('Note: Log Assistant v0.1 ')
st.subheader(f'Upload Data File', divider='rainbow')
st.sidebar.image('./Multi-layer-map_1.png', use_column_width=True)
 # Import the module
feature_target = ['GR', 'NPHI', 'PEF', 'RHOB']
loaded_model = joblib.load('./sonic_prediction_model.pkl')
well_info_placeholder = st.empty()
chart_placeholder = st.empty()
summary_placeholder = st.empty()
prediction_placeholder = st.empty()
new_content_placeholder = st.empty() 

#st.sidebar.subheader('Upload Data File')
mode = st.sidebar.selectbox('Upload Data File:', options=('Upload LAS File', 'Upload CSV file'))
# Create placeholders for dynamic content
file = st.sidebar.file_uploader('Upload the LAS file')

#if file':
#    file = st.sidebar.file_uploader('Upload the LAS file',)
if file:
    las_df, well_name, uwi, start_depth, stop_depth, step, company_name, date = log_utils.process_las_file(file)
    with well_info_placeholder.container():
        log_utils.display_well_info(st, well_name, uwi, start_depth, stop_depth, step, company_name, date)
        st.sidebar.title('Plot Setting')
        top_depth = st.sidebar.number_input('Top Depth', min_value=0.00, value=start_depth, step=100.00)
        bot_depth = st.sidebar.number_input('Base Depth', min_value=0.00, value=stop_depth, step=100.00)
        curves = las_df.columns.values
        gr_col = las_df.columns.get_loc('GR') if 'GR' in curves else 0
        pef_col = las_df.columns.get_loc('PEF') if 'PEF' in curves else 0
        den_col = las_df.columns.get_loc('RHOB') if 'RHOB' in curves else 0
        neu_col = las_df.columns.get_loc('NPHI') if 'NPHI' in curves else 0
        gr_curve = st.selectbox('Select the GAMMA RAY curve', curves, index=gr_col)
        pef_curve = st.selectbox('Select the Photoelectric Factor curve', curves, index=pef_col)
        den_curve = st.selectbox('Select the BULK DENSITY curve', curves, index=den_col)
        neu_curve = st.selectbox('Select the NEUTRON POROSITY curve', curves, index=neu_col)
        curve_list = [gr_curve, pef_curve, den_curve, neu_curve]

if st.sidebar.button('Display well logs'):
    with chart_placeholder.container():
        base, interval = log_utils.create_base_chart(las_df, bot_depth, top_depth)
        base2, interval2 = log_utils.create_base2_chart(las_df, bot_depth, top_depth)
        gr = log_utils.create_gr_chart(base, interval)
        rhob = log_utils.create_rhob_chart(base2, interval)
        nphi = log_utils.create_nphi_chart(base2, interval)
        pef = log_utils.create_pef_chart(base2, interval)
        #chart_nphi_rhob = (nphi + rhob)
        # Combine charts
        chart_nphi_rhob = alt.layer(rhob, nphi).resolve_scale(
            x='independent',
            ).properties().add_params(interval)
        combined_chart = log_utils.create_combined_chart(gr, chart_nphi_rhob, pef)
        st.altair_chart(combined_chart, use_container_width=True)


st.sidebar.divider()
with new_content_placeholder.container():
    st.sidebar.subheader('Select Prediction Model')
    model_selection = st.sidebar.radio('', options=('None', 'Sonic Log Prediction', 'Litho-Facies Prediction'))
    if model_selection=='Sonic Log Prediction':
        if 'las_df' in locals():
            if st.sidebar.button('Predict DT Log'):
                las_nan = las_df.copy()
                las_nan.dropna(axis=0, inplace=True)
                prediction = loaded_model.predict(las_nan[feature_target])
                las_nan['DT_predicted'] = prediction
                print(prediction)

                base, interval = log_utils.create_base_chart(las_nan, las_nan.DEPTH.max(), las_nan.DEPTH.min())
                base2, interval2 = log_utils.create_base2_chart(las_nan, las_nan.DEPTH.max(), las_nan.DEPTH.min())
                gr = log_utils.create_gr_chart(base, interval)
                rhob = log_utils.create_rhob_chart(base2, interval)
                nphi = log_utils.create_nphi_chart(base2, interval)
                pef = log_utils.create_pef_chart(base2, interval)
                dt = log_utils.create_dt_chart(base2, interval)
                chart_nphi_rhob = (nphi + rhob)
                combined_chart_dt = log_utils.create_combined_char_dt(gr, chart_nphi_rhob, pef, dt)
                st.altair_chart(combined_chart_dt, use_container_width=True)

  
