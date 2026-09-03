from pathlib import Path
import pandas as pd, numpy as np, streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bloom_engine import build_scored, validate_frames

st.set_page_config(page_title="BloomWatch Local",page_icon="🌊",layout="wide",initial_sidebar_state="expanded")
ROOT=Path(__file__).parent; DATA=ROOT/"data"

st.markdown('''<style>
.stApp{background:#f3f8fb;color:#17283a}.main .block-container{padding-top:1.4rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #dce8ef}[data-testid="stSidebar"] *{color:#1d3446!important}
.hero{background:linear-gradient(135deg,#075985,#0891b2 52%,#34d399);padding:30px;border-radius:24px;color:white;box-shadow:0 18px 45px rgba(7,89,133,.18);margin-bottom:18px}.hero h1{font-size:35px;margin:0 0 8px;font-weight:850}.hero p{font-size:15px;margin:0;opacity:.95}
.card{background:#fff;border:1px solid #dfe9ef;border-radius:18px;padding:17px 19px;box-shadow:0 7px 22px rgba(26,61,89,.05)}.label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#6b7d8c}.value{font-size:28px;font-weight:850;color:#13334b}.section{font-size:22px;font-weight:850;color:#153b55;margin:18px 0 10px}.note{background:#e9f8ff;border:1px solid #bde6f4;border-radius:12px;padding:11px 14px}
</style>''',unsafe_allow_html=True)

def metric(l,v): st.markdown(f'<div class="card"><div class="label">{l}</div><div class="value">{v}</div></div>',unsafe_allow_html=True)

@st.cache_data
def demo(): return pd.read_csv(DATA/'sample_water_quality.csv'),pd.read_csv(DATA/'sample_satellite_observations.csv')
water0,sat0=demo()
with st.sidebar:
    st.markdown('## 🌊 BloomWatch Local'); st.caption('Advanced algal-bloom early-warning intelligence')
    page=st.radio('Workspace',['Command Center','Risk Atlas','Site Deep Dive','Nutrient & Thermal','Satellite Watch','Hydrology Monitor','Response Planner','Data Lab','Exports'])
    st.markdown('---'); st.markdown('**100% LOCAL**'); st.write('No external APIs or cloud inference required.')

st.markdown('<div class="hero"><h1>🌊 BloomWatch Local</h1><p>Advanced harmful algal-bloom early-warning screening for lakes and reservoirs — multi-signal, explainable and locally processed.</p></div>',unsafe_allow_html=True)
with st.expander('📥 Local data intake',expanded=(page=='Data Lab')):
    c1,c2=st.columns(2)
    with c1: fw=st.file_uploader('Water quality CSV',type='csv',key='fw')
    with c2: fs=st.file_uploader('Satellite observation CSV',type='csv',key='fs')
    water=pd.read_csv(fw) if fw else water0.copy(); sat=pd.read_csv(fs) if fs else sat0.copy()
    problems=validate_frames(water,sat)
    if problems: st.error('Validation failed:\n\n'+'\n'.join('- '+p for p in problems)); st.stop()
    scored=build_scored(water,sat); st.success(f'Loaded {len(water)} sites and {len(sat)} satellite observations')

bands=scored.bloom_risk_band.value_counts().reindex(['Low','Moderate','High','Critical'],fill_value=0); avg=float(scored.bloom_risk_score.mean()); high=int((scored.bloom_risk_score>=50).sum()); crit=int((scored.bloom_risk_score>=75).sum())

if page=='Command Center':
    st.markdown('<div class="section">Waterbody Risk Command Center</div>',unsafe_allow_html=True)
    cs=st.columns(5)
    for c,(l,v) in zip(cs,[('Sites',len(scored)),('Mean risk',f'{avg:.1f}/100'),('High+',high),('Critical',crit),('Mean chlorophyll',f'{scored.chlorophyll_a_ug_l.mean():.1f} µg/L')]):
        with c: metric(l,v)
    a,b=st.columns([1,1.05])
    with a:
        fig=px.bar(bands.reset_index(),x='bloom_risk_band',y='count',text='count',color='bloom_risk_band',title='Current bloom-risk posture'); fig.update_layout(template='plotly_white',height=360); st.plotly_chart(fig,use_container_width=True)
    with b:
        fig=go.Figure(go.Indicator(mode='gauge+number',value=avg,title={'text':'Average screening risk'},gauge={'axis':{'range':[0,100]}})); fig.update_layout(template='plotly_white',height=360); st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns([1.15,1])
    with a:
        fig=px.scatter(scored,x='water_temp_c',y='chlorophyll_a_ug_l',size='total_phosphorus_mg_l',color='bloom_risk_band',hover_name='site_name',title='Thermal × chlorophyll signal'); fig.update_layout(template='plotly_white',height=400); st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown('#### Priority watchlist'); st.dataframe(scored.sort_values('watch_priority',ascending=False)[['site_id','site_name','bloom_risk_score','bloom_risk_band','watch_priority','total_phosphorus_mg_l']],use_container_width=True,hide_index=True)

elif page=='Risk Atlas':
    st.markdown('<div class="section">Risk Atlas</div>',unsafe_allow_html=True)
    atlas=scored.copy(); atlas['x']=np.arange(len(atlas))%4; atlas['y']=-(np.arange(len(atlas))//4)
    fig=px.scatter(atlas,x='x',y='y',size='bloom_risk_score',color='bloom_risk_band',text='site_name',hover_data=['site_id','watch_priority'],title='Local screening atlas'); fig.update_traces(textposition='top center'); fig.update_layout(template='plotly_white',height=570,xaxis_visible=False,yaxis_visible=False); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(scored.sort_values('bloom_risk_score',ascending=False)[['site_id','site_name','bloom_risk_score','bloom_risk_band','thermal_pressure','nutrient_pressure','rainfall_runoff_pressure','low_flow_pressure','chlorophyll_pressure']],use_container_width=True,hide_index=True)

elif page=='Site Deep Dive':
    st.markdown('<div class="section">Site Deep Dive</div>',unsafe_allow_html=True)
    sid=st.selectbox('Waterbody',list(scored.site_id),format_func=lambda x: scored.loc[scored.site_id==x,'site_name'].iloc[0]); r=scored.loc[scored.site_id==sid].iloc[0]
    cs=st.columns(5)
    for c,(l,v) in zip(cs,[('Risk',r.bloom_risk_score),('Band',r.bloom_risk_band),('Temperature',f'{r.water_temp_c:.1f} °C'),('Chlorophyll',f'{r.chlorophyll_a_ug_l:.1f} µg/L'),('Flow',f'{r.flow_m3_s:.1f} m³/s')]):
        with c: metric(l,v)
    a,b=st.columns(2)
    with a:
        names=['Thermal','Nutrients','Rainfall','Low flow','Chlorophyll','Turbidity','Satellite']; vals=[r.thermal_pressure,r.nutrient_pressure,r.rainfall_runoff_pressure,r.low_flow_pressure,r.chlorophyll_pressure,r.turbidity_pressure,r.satellite_pressure]; fig=go.Figure(go.Bar(x=vals,y=names,orientation='h')); fig.update_layout(template='plotly_white',height=400,xaxis_range=[0,100],title='Risk-driver fingerprint'); st.plotly_chart(fig,use_container_width=True)
    with b:
        fig=go.Figure(go.Indicator(mode='gauge+number',value=r.bloom_risk_score,title={'text':'Site bloom-risk score'},gauge={'axis':{'range':[0,100]}})); fig.update_layout(template='plotly_white',height=400); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(sat[sat.site_id==sid],use_container_width=True,hide_index=True)

elif page=='Nutrient & Thermal':
    st.markdown('<div class="section">Nutrient & Thermal Signals</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        fig=px.scatter(scored,x='total_nitrogen_mg_l',y='total_phosphorus_mg_l',size='chlorophyll_a_ug_l',color='bloom_risk_band',hover_name='site_name',title='Nutrients × chlorophyll'); fig.update_layout(template='plotly_white',height=430); st.plotly_chart(fig,use_container_width=True)
    with b:
        fig=px.scatter(scored,x='water_temp_c',y='turbidity_ntu',size='rainfall_7d_mm',color='bloom_risk_band',hover_name='site_name',title='Temperature × turbidity'); fig.update_layout(template='plotly_white',height=430); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(scored.sort_values('nutrient_pressure',ascending=False)[['site_id','site_name','total_nitrogen_mg_l','total_phosphorus_mg_l','nutrient_pressure','chlorophyll_a_ug_l']],use_container_width=True,hide_index=True)

elif page=='Satellite Watch':
    st.markdown('<div class="section">Satellite Watch</div>',unsafe_allow_html=True); st.markdown('<div class="note">Satellite observations are supplied locally. No remote imagery service is contacted by this application.</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        fig=px.scatter(sat,x='cloud_cover_pct',y='ndci_index',color='ndci_index',hover_data=['site_id','capture_date'],title='NDCI signal vs cloud cover'); fig.update_layout(template='plotly_white',height=430); st.plotly_chart(fig,use_container_width=True)
    with b: st.dataframe(scored.sort_values('satellite_pressure',ascending=False)[['site_id','site_name','ndci_mean','cloud_cover_mean','satellite_observations','satellite_pressure']],use_container_width=True,hide_index=True,height=430)

elif page=='Hydrology Monitor':
    st.markdown('<div class="section">Hydrology Monitor</div>',unsafe_allow_html=True); fh=pd.read_csv(DATA/'sample_flow_history.csv'); rh=pd.read_csv(DATA/'sample_rainfall_history.csv'); sid=st.selectbox('Waterbody',list(scored.site_id),format_func=lambda x: scored.loc[scored.site_id==x,'site_name'].iloc[0])
    a,b=st.columns(2)
    with a: q=fh[fh.site_id==sid]; fig=px.line(q,x='week_label',y='flow_m3_s',markers=True,title='Local flow history'); fig.update_layout(template='plotly_white',height=380); st.plotly_chart(fig,use_container_width=True)
    with b: q=rh[rh.site_id==sid]; fig=px.bar(q,x='week_label',y='rainfall_mm',title='Local rainfall history'); fig.update_layout(template='plotly_white',height=380); st.plotly_chart(fig,use_container_width=True)

elif page=='Response Planner':
    st.markdown('<div class="section">Response Planner</div>',unsafe_allow_html=True); q=scored.copy(); q['recommended_review']=np.select([q.bloom_risk_score>=75,q.bloom_risk_score>=50,q.nutrient_pressure>=60,q.low_flow_pressure>=60],['Immediate confirmatory sampling / field review','Increase monitoring cadence and review local signals','Investigate nutrient/runoff contributors','Review inflow/outflow and low-flow conditions'],default='Routine monitoring'); q['priority']=q.watch_priority
    st.dataframe(q.sort_values('priority',ascending=False)[['site_id','site_name','priority','bloom_risk_band','recommended_review','thermal_pressure','nutrient_pressure','satellite_pressure']].head(15),use_container_width=True,hide_index=True); st.info('Screening aid only; does not determine toxins, species, regulatory status, or public-health decisions.')

elif page=='Data Lab':
    st.markdown('<div class="section">Data Lab</div>',unsafe_allow_html=True); st.write('Water quality fields'); st.code(', '.join(['site_id','site_name','water_temp_c','total_nitrogen_mg_l','total_phosphorus_mg_l','rainfall_7d_mm','flow_m3_s','chlorophyll_a_ug_l','turbidity_ntu'])); st.write('Satellite fields'); st.code(', '.join(['site_id','capture_date','ndci_index','surface_reflectance','cloud_cover_pct'])); st.dataframe(water,use_container_width=True,hide_index=True)

else:
    st.markdown('<div class="section">Reports & Export</div>',unsafe_allow_html=True); st.dataframe(scored.sort_values('bloom_risk_score',ascending=False)[['site_id','site_name','bloom_risk_score','bloom_risk_band','watch_priority','thermal_pressure','nutrient_pressure','rainfall_runoff_pressure','low_flow_pressure','chlorophyll_pressure','satellite_pressure']],use_container_width=True,hide_index=True); st.download_button('Download bloom-risk intelligence CSV',scored.to_csv(index=False).encode(),file_name='bloomwatch_risk_intelligence.csv',mime='text/csv'); st.download_button('Download satellite observations CSV',sat.to_csv(index=False).encode(),file_name='bloomwatch_satellite_observations.csv',mime='text/csv')
