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
