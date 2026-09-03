from pathlib import Path
import pandas as pd
from bloom_engine import build_scored,validate_frames
R=Path(__file__).parent
w=pd.read_csv(R/'data/sample_water_quality.csv'); s=pd.read_csv(R/'data/sample_satellite_observations.csv')
e=validate_frames(w,s); assert not e,e
o=build_scored(w,s); assert len(o)==len(w); assert o.bloom_risk_score.between(0,100).all(); assert o.watch_priority.between(0,100).all()
print('PASS: BloomWatch local algal-bloom screening'); print(f'Sites: {len(o)}'); print(f'Risk range: {o.bloom_risk_score.min():.1f} - {o.bloom_risk_score.max():.1f}'); print(f'High/Critical: {(o.bloom_risk_score>=50).sum()}')
