from __future__ import annotations
import numpy as np
import pandas as pd

REQUIRED_WATER=["site_id","site_name","water_temp_c","total_nitrogen_mg_l","total_phosphorus_mg_l","rainfall_7d_mm","flow_m3_s","chlorophyll_a_ug_l","turbidity_ntu"]
REQUIRED_SAT=["site_id","capture_date","ndci_index","surface_reflectance","cloud_cover_pct"]

def num(x, default=0.0):
    try:
        v=float(x)
        return default if not np.isfinite(v) else v
    except (TypeError,ValueError): return default

def clamp(x,lo=0,hi=100): return float(np.clip(num(x),lo,hi))

def band(s):
    s=num(s)
    return "Low" if s<25 else "Moderate" if s<50 else "High" if s<75 else "Critical"

def build_scored(water:pd.DataFrame,satellite:pd.DataFrame|None=None):
    df=water.copy()
    t=pd.to_numeric(df.water_temp_c,errors="coerce").fillna(0)
    n=pd.to_numeric(df.total_nitrogen_mg_l,errors="coerce").fillna(0)
    p=pd.to_numeric(df.total_phosphorus_mg_l,errors="coerce").fillna(0)
    rain=pd.to_numeric(df.rainfall_7d_mm,errors="coerce").fillna(0)
    flow=pd.to_numeric(df.flow_m3_s,errors="coerce").fillna(0)
    chl=pd.to_numeric(df.chlorophyll_a_ug_l,errors="coerce").fillna(0)
    turb=pd.to_numeric(df.turbidity_ntu,errors="coerce").fillna(0)
    thermal=np.clip((t-18)*3,0,100)
    nutrient=np.clip(n*10+p*55,0,100)
    rainfall=np.clip(rain*1.8,0,100)
    lowflow=np.clip((8-flow)*11,0,100)
    chlorophyll=np.clip(chl*2.2,0,100)
    turbidity=np.clip(turb*1.5,0,100)
    base=.24*thermal+.27*nutrient+.13*rainfall+.15*lowflow+.16*chlorophyll+.05*turbidity
    for name,val in [("thermal_pressure",thermal),("nutrient_pressure",nutrient),("rainfall_runoff_pressure",rainfall),("low_flow_pressure",lowflow),("chlorophyll_pressure",chlorophyll),("turbidity_pressure",turbidity)]: df[name]=np.round(val,1)
    df["bloom_risk_score"]=np.round(base,1)
    if satellite is not None and not satellite.empty:
        sat=satellite.copy(); sat["ndci_index"]=pd.to_numeric(sat.ndci_index,errors="coerce").fillna(0); sat["cloud_cover_pct"]=pd.to_numeric(sat.cloud_cover_pct,errors="coerce").fillna(100)
        ag=sat.groupby("site_id",as_index=False).agg(ndci_mean=("ndci_index","mean"),cloud_cover_mean=("cloud_cover_pct","mean"),satellite_observations=("site_id","count"))
        df=df.merge(ag,on="site_id",how="left")
        df["ndci_mean"]=df.ndci_mean.fillna(0); df["cloud_cover_mean"]=df.cloud_cover_mean.fillna(100); df["satellite_observations"]=df.satellite_observations.fillna(0).astype(int)
        df["satellite_pressure"]=np.round(np.clip((df.ndci_mean+.1)*320,0,100),1)
    else:
        df["ndci_mean"]=0.0; df["cloud_cover_mean"]=100.0; df["satellite_observations"]=0; df["satellite_pressure"]=0.0
    df["bloom_risk_score"]=np.round(np.clip(.92*df.bloom_risk_score+.08*df.satellite_pressure,0,100),1)
    df["bloom_risk_band"]=df.bloom_risk_score.apply(band)
    df["watch_priority"]=np.round(.65*df.bloom_risk_score+.35*df.chlorophyll_pressure,1)
    return df

def validate_frames(water,satellite=None):
    out=[]
    for c in REQUIRED_WATER:
        if c not in water.columns: out.append(f"water: missing '{c}'")
    if satellite is not None:
        for c in REQUIRED_SAT:
            if c not in satellite.columns: out.append(f"satellite: missing '{c}'")
    if "site_id" in water.columns:
        if water.site_id.isna().any() or (water.site_id.astype(str).str.strip()=="").any(): out.append("water: blank site_id")
        if water.site_id.duplicated().any(): out.append("water: duplicate site_id values")
    return out
