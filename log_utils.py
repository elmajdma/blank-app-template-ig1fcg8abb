# log_utils.py

import altair as alt
import lasio
import pandas as pd
from tempfile import NamedTemporaryFile

def process_las_file(file):
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

        return las_df, well_name, uwi, start_depth, stop_depth, step, company_name, date

def process_csv_file(file):
    if file is not None:
        tfile = NamedTemporaryFile(delete=False)
        tfile.write(file.read())
        las_df = pd.read_csv(tfile.name)
        las_df.insert(0, 'DEPTH', las_df.index)
        las_df.reset_index(drop=True, inplace=True)
        return las_df

def display_well_info(st, well_name, uwi, start_depth, stop_depth, step, company_name, date):
    st.subheader('Well Information')
    st.text(f'Well Name: {well_name}')
    st.text(f'UWI: {uwi}')
    st.text(f'Start Depth: {start_depth}')
    st.text(f'Stop Depth: {stop_depth}')
    st.text(f'Step: {step}')
    st.text(f'Company: {company_name}')
    st.text(f'Logging Date: {date}')

def create_base_chart(data, bot_depth, top_depth):
    interval = alt.selection_interval()
    base = alt.Chart(data).mark_line(point=False).encode(
        alt.Y('DEPTH:Q', scale=alt.Scale(domain=[bot_depth, top_depth])),
    ).properties(
        width=250,
        height=2000,
    ).add_params(interval)
    return base, interval

def create_base2_chart(data, bot_depth, top_depth):
    interval = alt.selection_interval()
    base = alt.Chart(data).mark_line(point=False).encode(
        alt.Y('DEPTH:Q', scale=alt.Scale(domain=[bot_depth, top_depth]),
              axis=alt.Axis(labels=False), title='')).properties(
        width=250,
        height=2000,
    ).add_params(interval)
    return base, interval

def create_gr_chart(base, interval):
    gr = base.mark_line(interpolate='monotone', color='green', clip=True).encode(
        alt.X('GR:Q', scale=alt.Scale(domain=[0, 200]), axis=alt.Axis(
            labelAngle=0, title='GR', orient='top')),
        order='DEPTH',
        tooltip='GR:Q',
    ).properties().add_params(interval)
    return gr

def create_rhob_chart(base2, interval):
    rhob = base2.mark_line(interpolate='monotone', color='red', clip=True).encode(
        alt.X('RHOB:Q', scale=alt.Scale(domain=[1.9, 3]), axis=alt.Axis(title='RHOB', orient='top')),
        color=alt.value('red'),
        order='DEPTH',
    ).properties().add_params(interval)
    return rhob

def create_nphi_chart(base2, interval):
    nphi = base2.mark_line(interpolate='monotone', color='yellow', clip=True).encode(
        alt.X('NPHI:Q', scale=alt.Scale(domain=[0.44, -0.2]), axis=alt.Axis(title='NPHI', orient='top', titleY=-30)),
        color=alt.value('yellow'),
        order='DEPTH',
    ).properties().add_params(interval)
    return nphi

def create_pef_chart(base2, interval):
    pef = base2.mark_line(interpolate='monotone', color='brown', clip=True).encode(
        alt.X('PEF:Q', scale=alt.Scale(domain=[1, 15]), axis=alt.Axis(labelAngle=0, title='PEF', orient='top')),
        color=alt.value('brown'),
        order='DEPTH',
    ).properties().add_params(interval)
    return pef

def create_dt_chart(base2, interval):
    dt = base2.mark_line(interpolate='monotone', color='yellow', clip=True).encode(
        alt.X('DT_predicted:Q', scale=alt.Scale(domain=[140, 40]), axis=alt.Axis(labelAngle=0, title='DT Predicted', orient='top')),
        color=alt.value('yellow'),
        order='DEPTH',
    ).properties().add_params(interval)
    return dt

def create_combined_char_dt(gr, chart_nphi_rhob, pef, dt):
    combined_chart = gr | chart_nphi_rhob | pef | dt
    combined_chart = combined_chart.configure_header(
        titleColor='white',
        titleFontSize=16,
        labelColor='red',
        labelFontSize=14,
    )
    return combined_chart

def create_combined_chart(gr, chart_nphi_rhob, pef):
    combined_chart = gr | chart_nphi_rhob | pef
    combined_chart = combined_chart.configure_header(
        titleColor='white',
        titleFontSize=16,
        labelColor='red',
        labelFontSize=14,
    )
    return combined_chart
