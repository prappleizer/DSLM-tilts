import pandas as pd
import streamlit as st
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from astropy.coordinates import Distance
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
import plotly.express as px 
import plotly.graph_objects as go
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

def shift(wavelen, theta, n_2, n_1) :
    """Calculates the wavelength shift given tilt and filter parameters"""
    new = wavelen*np.sqrt(1.-((n_1/n_2)*np.sin(theta*np.pi / 180.))**2)
    return new

def get_filterwidth_ha(tilt,FOV_size,cwl, filterwidth = 8,):
    shift_cent = shift(cwl, tilt, 1.98,1)
    shift_up   = shift(cwl, tilt+FOV_size/2., 1.98,1)
    shift_down = shift(cwl, tilt-FOV_size/2., 1.98,1)

    low1  = (shift_cent - filterwidth/2.)
    high1 = (shift_cent + filterwidth/2.)

    low2  = (shift_up - filterwidth/2.)
    high2 = (shift_up + filterwidth/2.)

    low3  = (shift_down - filterwidth/2.)
    high3 = (shift_down + filterwidth/2.)
    return [[low1,high1],[low2,high2],[low3,high3]]

def get_filterwidth_oiii(tilt,FOV_size,cwl, filterwidth = 8,):
    shift_cent = shift(cwl, tilt, 2.12,1)
    shift_up   = shift(cwl, tilt+FOV_size/2., 2.12,1)
    shift_down = shift(cwl, tilt-FOV_size/2., 2.12,1)

    low1  = (shift_cent - filterwidth/2.)
    high1 = (shift_cent + filterwidth/2.)

    low2  = (shift_up - filterwidth/2.)
    high2 = (shift_up + filterwidth/2.)

    low3  = (shift_down - filterwidth/2.)
    high3 = (shift_down + filterwidth/2.)
    return [[low1,high1],[low2,high2],[low3,high3]]    

c=300000.


st.title("DSLM Filter Tilt Calculator")
st.header("Instructions")
st.markdown("Set the galaxy velocity using the side bar, then use the tilt slider to explore how the tilt affects the bandpass.")
st.markdown("As you move to larger tilts (lower wavelength), the shaded regions shows the bandpass at the left, middle, and right hand edge of the FOV selected. This gives an idea at each tilt of how large a contiguous FOV you can observe while still catching the given line.")

#st.sidebar.text_input("Galaxy Name", key="gal_name",value="")
gal_vel = st.sidebar.text_input("Galaxy Velocity (km/s)", key="gal_velocity",help="enter velocity here",value=0.0)
gal_vel = float(gal_vel)
ha_wl = 6562.801*(1+gal_vel/c)
oiii_1_wl = 4958.911*(1+gal_vel/c)
oiii_2_wl = 5006.843*(1+gal_vel/c)
nii_1_wl = 6548.05*(1+gal_vel/c)
nii_2_wl = 6583.45*(1+gal_vel/c)



ha_tilt = st.sidebar.slider('H-alpha Filter Tilt',min_value=0.0,max_value=20.0,value=10.0,step=0.1,key='ha_tilt') 
oiii_tilt = st.sidebar.slider('[OIII] Filter Tilt',min_value=0.0,max_value=20.0,value=10.0,step=0.1,key='oiii_tilt') 
width = 0.8
fov = st.sidebar.slider('Field of View',min_value=0.25,max_value=2.0,step=0.25,value=1.0,key='fov')
galaxy_velocity = float(st.session_state.gal_velocity)
st.subheader('Currently Selected Parameters')
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Galaxy Velocity", value=f"{st.session_state.gal_velocity} km/s", delta="")
col2.metric(label="Halpha Tilt", value=f"{ha_tilt} nm", delta="")
col3.metric(label="[OIII] Tilt", value=f"{oiii_tilt} nm", delta="")
col4.metric(label='FOV',value=f"{fov}°",delta="")




c = 300000. # km/s


filter_bounds_ha = get_filterwidth_ha(ha_tilt,fov,cwl=6647)
filter_bounds_oiii = get_filterwidth_oiii(oiii_tilt,fov,cwl=5071)



fig1 = go.Figure(layout_xaxis_range=[nii_1_wl-50.0,nii_2_wl+50.0],layout_yaxis_range=[0,2.5])
fig2 = go.Figure(layout_xaxis_range=[oiii_1_wl-50.0,oiii_2_wl+50.0],layout_yaxis_range=[0,2.5])

fig1.add_shape(type="rect",
    x0=filter_bounds_ha[0][0], y0=0, x1=filter_bounds_ha[0][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="green",
    opacity=0.9,
)
fig1.add_shape(type="rect",
    x0=filter_bounds_ha[1][0], y0=0, x1=filter_bounds_ha[1][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="orange",
    opacity=0.2,
)
fig1.add_shape(type="rect",
    x0=filter_bounds_ha[2][0], y0=0, x1=filter_bounds_ha[2][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="orange",
    opacity=0.2,
)


fig1.add_trace(go.Scatter(
    x=[nii_1_wl,ha_wl,nii_2_wl],
    y=[0.6, 2.1, 1.1],
    text=["[NII]",
          "Hα",
          "[NII]"],
    mode="text",
    
))


fig1.add_shape(type="line",
    x0=ha_wl, y0=0, x1=ha_wl, y1=2,
    line=dict(color="#B82E2E",width=6)
)
fig1.add_shape(type="line",
    x0=nii_1_wl, y0=0, x1=nii_1_wl, y1=0.5,
    line=dict(color="#B82E2E",width=4)
)
fig1.add_shape(type="line",
    x0=nii_2_wl, y0=0, x1=nii_2_wl, y1=1.0,
    line=dict(color="#B82E2E",width=4)
)
fig2.add_trace(go.Scatter(
    x=[oiii_1_wl,oiii_2_wl],
    y=[2.1,2.1],
    text=["[OIII]4958",
          "[OIII] 5007"],
    mode="text",
))

fig2.add_shape(type="rect",
    x0=filter_bounds_oiii[0][0], y0=0, x1=filter_bounds_oiii[0][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="green",
    opacity=0.9,
)
fig2.add_shape(type="rect",
    x0=filter_bounds_oiii[1][0], y0=0, x1=filter_bounds_oiii[1][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="orange",
    opacity=0.2,
)
fig2.add_shape(type="rect",
    x0=filter_bounds_oiii[2][0], y0=0, x1=filter_bounds_oiii[2][1], y1=2,
    line=dict(
        color="black",
        width=2,
    ),
    fillcolor="orange",
    opacity=0.2,
)



fig2.add_shape(type="line",
    x0=oiii_1_wl, y0=0, x1=oiii_1_wl, y1=2,
    line=dict(color="RoyalBlue",width=6)
)
fig2.add_shape(type="line",
    x0=oiii_2_wl, y0=0, x1=oiii_2_wl, y1=2,
    line=dict(color="RoyalBlue",width=6)
)

fig1.add_shape(type="rect",
    x0=6653, y0=0, x1=10000, y1=2,
    line=dict(
        color="gray",
        width=2,
    ),
    fillcolor="gray",
    opacity=0.3
)





fig2.add_shape(type="rect",
    x0=5075, y0=0, x1=10000, y1=2,
    line=dict(
        color="gray",
        width=2,
    ),
    fillcolor="gray",
    opacity=0.3,
)


fig1.update_shapes(dict(xref='x', yref='y'),)
fig2.update_shapes(dict(xref='x', yref='y'),)
fig1.update_layout(height=800,font=dict(
        family="Courier New, monospace",
        size=30,  # Set the font size here
        color="black"
    ))
fig2.update_layout(height=800,font=dict(
        family="Courier New, monospace",
        size=30,  # Set the font size here
        color="black"
    ))
st.divider()
st.write('### H-alpha Visualizer')
st.plotly_chart(fig1, use_container_width=True)
st.write('### [OIII] Visualizer')
st.plotly_chart(fig2, use_container_width=True)
