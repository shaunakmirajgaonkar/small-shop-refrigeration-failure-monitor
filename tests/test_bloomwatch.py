from pathlib import Path
import pandas as pd
from bloom_engine import build_scored,validate_frames
R=Path(__file__).parents[1]
def test_schema():
    w=pd.read_csv(R/'data/sample_water_quality.csv'); s=pd.read_csv(R/'data/sample_satellite_observations.csv'); assert validate_frames(w,s)==[]
def test_bounds():
    w=pd.read_csv(R/'data/sample_water_quality.csv'); s=pd.read_csv(R/'data/sample_satellite_observations.csv'); o=build_scored(w,s); assert o.bloom_risk_score.between(0,100).all(); assert o.watch_priority.between(0,100).all()
def test_unique_sites():
    w=pd.read_csv(R/'data/sample_water_quality.csv'); assert not w.site_id.duplicated().any()
