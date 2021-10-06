import pandas as pd
import streamlit as st
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib
from astropy.coordinates import Distance
from astropy import units as u
from astropy.coordinates import SkyCoord
from mpl_toolkits.mplot3d import Axes3D
from astropy.io import fits

plt.style.use('seaborn-dark-palette')
plt.style.use('ggplot')
font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 16}

matplotlib.rc('font', **font)


def plotfilt(ax,center,width,color='black',label='',linestyle='-',height=1):
    """Plots black box around filter bandpass (in center of FOV)"""
    ax.plot([center-width/2,center+width/2,center+width/2,center-width/2,center-width/2],[0,0,height,height,0],
           linewidth=2,color=color,linestyle=linestyle)
    ax.text(center,height+.2,label,horizontalalignment='center',fontsize='large')


def shift(wavelen, theta, n_2, n_1) :
    """Calculates the wavelength shift given tilt and filter parameters"""
    new = wavelen*np.sqrt(1.-((n_1/n_2)*np.sin(theta*np.pi / 180.))**2)
    return new-wavelen

def plotfilter(tilt,ax,cwl=6599,height=1,label='', filterwidth = 3.,FOV_size =1):
    'Plot shaded regions to show the width of the filter'
#     filterwidth = 3. #nm
    #FOV_size = 1. # degrees
    shift_cent = shift(659.9, tilt, eff_index_of_refr_TWEAK,1)
    shift_up   = shift(659.9, tilt+FOV_size/2., eff_index_of_refr_TWEAK,1)
    shift_down = shift(659.9, tilt-FOV_size/2., eff_index_of_refr_TWEAK,1)

    low  = (shift_cent - filterwidth/2.)*10.
    high = (shift_cent + filterwidth/2.)*10.

    ax.fill_between([low+cwl,high+cwl],0,height, alpha=0.8)
    
    low  = (shift_up - filterwidth/2.)*10.
    high = (shift_up + filterwidth/2.)*10.
    ax.fill_between([low+cwl,high+cwl],0,height,alpha=0.3)

    low  = (shift_down - filterwidth/2.)*10.
    high = (shift_down + filterwidth/2.)*10.
    ax.fill_between([low+cwl,high+cwl],0,height,alpha=0.3)
    
    ax.text(shift_cent*10,height+.2,label,horizontalalignment='center')

def plotlines(ax,v):
    plotfilt(ax,6563*(1+v/c),1,color='red',label=r'H$\alpha$')
    ax.text(0.01,0.98,f'Ha at {6563*(1+v/c):.1f} Angstrom',transform=ax.transAxes,va='top',ha='left',fontsize='x-large')
    plotfilt(ax,6585*(1+v/c),1,color='green',label= '[NII]')
    plotfilt(ax,6550*(1+v/c),1,color='green',label= '[NII]')
#     plotfilt(ax,6548*(1+v/c),1,color='cyan',label= '[NII]')


def ha_at(v):
    return 6563*(1+float(v)/300000.)



st.title("DSLM Filter Tilt Calculator")
#st.markdown("Welcome to this in-depth introduction to [...].")
st.header("Instructions")
st.markdown("Set the galaxy velocity and desired filter width using the side bar, then use the tilt slider to explore how the tilt affects the bandpass.")
st.markdown("As you move to larger tilts (lower wavelength), the shaded regions shows the bandpass at the left, middle, and right hand edge of the FOV of the instrument.")

#st.sidebar.text_input("Galaxy Name", key="gal_name",value="")
st.sidebar.text_input("Galaxy Velocity (km/s)", key="gal_velocity",help="enter velocity here",value=0.0)
x = st.sidebar.slider('Tilt',min_value=0.0,max_value=20.0,value=10.0,step=0.5,key='tilt') 
#w = st.slider('Filter Width',min_value=0.8,max_value=3.0,value=3.0,step=2.2,key='fwidth') 
width = st.sidebar.select_slider('Select Filter Width [nm]', options=[0.8,1,1.5,2,2.5,3], value=3, key='fwidth')
fov = st.sidebar.slider('Field of View',min_value=0.25,max_value=2.0,step=0.25,value=1.0,key='fov')
galaxy_velocity = float(st.session_state.gal_velocity)
st.subheader('Currently Selected Parameters')
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Galaxy Velocity", value=f"{st.session_state.gal_velocity} km/s", delta="")
col2.metric(label="Bandpass", value=f"{st.session_state.fwidth} nm", delta="")
col3.metric(label="Filter Tilt", value=f"{st.session_state.tilt}°", delta="")
#col4.metric(label='Hα at',value=f"{ha_at(st.session_state.gal_velocity):.0f} Å",delta="")
col4.metric(label='FOV',value=f"{st.session_state.fov}°",delta="")
#st.markdown(f'Galaxy Velocity: {st.session_state.gal_velocity} km/s')
#st.markdown(f'Filter Width: {st.session_state.fwidth*10} Angstrom | Filter Tilt: {st.session_state.tilt} degrees')
# df = pd.DataFrame()
# df['Galaxy Velocity [km/s]'] = st.session_state.gal_velocity
# df['Filter Width [nm]'] = st.session_state.fwidth
# df['Filter Tilt [deg]'] = st.session_state.tilt 
# st.dataframe(df)


eff_index_of_refr_TWEAK = 2.1 # tweaked to fit AstroDon's values
tilt = np.arange(0,30.1,0.1)
shiftresult = shift(659.9, tilt, eff_index_of_refr_TWEAK,1)
start=6500.; end=6620.
c = 300000. # km/s




f,ax = plt.subplots(figsize=(13.,8.0))


ax.set_ylim(0,2)
ax.set_xlim(start,end)
#ax.set_ylabel('Flux (sky)')
ax.set_xlabel('wavelength (Angstrom)')
ax.set_yticklabels([])
plotlines(ax,float(st.session_state.gal_velocity))

plotfilt(ax,6599+10*shiftresult[tilt==st.session_state.tilt],st.session_state.fwidth*10.,color='black',
         label= 'Tilt=%s deg'%st.session_state.tilt,height=1.5)
plotfilter(st.session_state.tilt,ax,height=1.5,filterwidth=st.session_state.fwidth,FOV_size =st.session_state.fov)

#ax.set_title(r"%s (%s km/s) | Filter width: %s $\mathrm{\AA}$ | "%(st.session_state.gal_name,st.session_state.gal_velocity,st.session_state.fwidth*10.)+
#              " Filter CWL: 6599 $\mathrm{\AA}$ | Field-of-view: 1.8 deg \n")

# ax2.plot(tilt,shiftresult,'k-',label='theoretical')
# ax2.axvline(float(st.session_state.tilt),color='r',lw=3.5,alpha=0.5,label='current tilt')
# ax2.legend()
# ax2.set_xlabel('Tilt Angle [deg]',fontsize='large')
# ax2.set_xlabel('Tilt Angle [deg]',fontsize='large')

plt.tight_layout()
st.write(f)