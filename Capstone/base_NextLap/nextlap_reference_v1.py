"""Reference data and model functions for the NextLap capstone."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ['current_lap_s', 'recent_mean_s', 'current_lap_number', 'current_tyre_life']
CATEGORICAL = ['current_compound', 'current_team']
TARGET = 'next_lap_s'
KEYS = ['season', 'round', 'driver_number']
BOOLEAN = ['is_accurate', 'pit_in', 'pit_out', 'deleted']


def locate_root(start=None):
    start = Path.cwd() if start is None else Path(start)
    candidates = [start, Path(__file__).resolve().parent,
                  start / 'IIT414W_T3_2026/02_diseno_evaluacion/ControlAplicado_NextLap_v2']
    for candidate in candidates:
        if (candidate / 'data/source_manifest_v2.json').is_file():
            return candidate.resolve()
    raise FileNotFoundError('Keep the notebook with nextlap_support_v2.py and data/. Run fetch_2026_data_v2.py first if the real snapshots are missing.')


def load_snapshots(root):
    root = Path(root)
    manifest = json.loads((root / 'data/source_manifest_v2.json').read_text(encoding='utf-8'))
    if manifest.get('synthetic') is not False or manifest.get('season') != 2026:
        raise ValueError('This notebook requires the verified real 2026 manifest.')
    frames=[]
    for event in manifest['events']:
        path = root / event['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != event['sha256']:
            raise ValueError(f'Snapshot checksum changed: {path.name}. Version the changed data explicitly.')
        frame = pd.read_csv(path, dtype={'driver_number':str,'track_status':str})
        for column in BOOLEAN:
            frame[column] = frame[column].astype(str).str.lower().eq('true')
        if len(frame) != event['rows'] or not frame['season'].eq(2026).all():
            raise ValueError(f'Unexpected race data: {path.name}')
        frames.append(frame)
    raw = pd.concat(frames, ignore_index=True).sort_values(KEYS+['lap_number']).reset_index(drop=True)
    if raw.duplicated(KEYS+['lap_number']).any():
        raise ValueError('Duplicate driver-lap keys in the original timing.')
    return raw, manifest


def build_pairs(raw, history_window=3):
    """Build target on the original timeline BEFORE selecting clean pairs.

    History includes lap t, which has just finished; rolling never sees t+1.
    No rolling history crosses drivers, races or tyre stints.
    """
    if not isinstance(history_window,int) or history_window<1:
        raise ValueError('history_window must be a positive integer.')
    data=raw.sort_values(KEYS+['lap_number']).reset_index(drop=True).copy()
    grouped=data.groupby(KEYS,sort=False)
    following=['lap_number','lap_time_s','end_time_s','stint','compound','track_status',*BOOLEAN]
    for column in following:
        data['next_'+column]=grouped[column].shift(-1)
    data['current_clean']=(data.lap_number.gt(1)&data.lap_time_s.gt(0)&data.is_accurate&~data.pit_in&~data.pit_out&~data.deleted&data.track_status.eq('1'))
    # A bad already-observed lap does not become a hidden recent-history input.
    data['history_value']=data.lap_time_s.where(data.current_clean)
    stint_keys=KEYS+['stint']
    data['recent_mean_s']=data.groupby(stint_keys,dropna=False,sort=False)['history_value'].transform(lambda s:s.rolling(history_window,min_periods=1).mean())
    data['recent_count']=data.groupby(stint_keys,dropna=False,sort=False)['history_value'].transform(lambda s:s.rolling(history_window,min_periods=1).count())
    next_clean=(data['next_lap_number'].gt(1)&data['next_lap_time_s'].gt(0)&data['next_is_accurate'].eq(True)&data['next_pit_in'].eq(False)&data['next_pit_out'].eq(False)&data['next_deleted'].eq(False)&data['next_track_status'].eq('1'))
    data['same_stint']=data.stint.eq(data.next_stint)&data.compound.eq(data.next_compound)&data.stint.notna()&data.compound.notna()
    data['clean_pair']=data.current_clean&next_clean&data.same_stint
    # No filtering then shift: t+1 must be the actual next numbered lap.
    eligible=(data.lap_number.ge(2)&data.next_lap_number.eq(data.lap_number+1)&data.lap_time_s.gt(0)&data.next_lap_time_s.gt(0)&data.next_end_time_s.gt(data.end_time_s))
    pairs=data.loc[eligible].copy().rename(columns={
        'lap_number':'current_lap_number','lap_time_s':'current_lap_s',
        'tyre_life':'current_tyre_life','compound':'current_compound',
        'team':'current_team','next_lap_time_s':TARGET,
    })
    pairs['pair_id']=(pairs.season.astype(str)+'-R'+pairs['round'].astype(str)+'-'+pairs.driver_number+'-L'+pairs.current_lap_number.astype(int).astype(str))
    if pairs.pair_id.duplicated().any():
        raise ValueError('Pair keys are not unique.')
    assert pairs.next_lap_number.eq(pairs.current_lap_number+1).all()
    assert pairs.next_end_time_s.gt(pairs.end_time_s).all()
    return pairs.reset_index(drop=True)


def split_by_race(pairs, train_rounds, validation_rounds, test_rounds):
    sets=[set(train_rounds),set(validation_rounds),set(test_rounds)]
    if any(sets[i]&sets[j] for i in range(3) for j in range(i+1,3)):
        raise ValueError('A race cannot appear in two splits.')
    if any(not item for item in sets):
        raise ValueError('Provide nonempty train, validation and test race lists.')
    observed=set(pairs['round'].astype(int))
    if set.union(*sets)-observed:
        raise ValueError('A requested race is missing from the real snapshot.')
    frames=[pairs.loc[pairs['round'].isin(s)].copy() for s in sets]
    if any(frame.empty for frame in frames):
        raise ValueError('A split has no eligible rows.')
    for earlier,later in zip(frames,frames[1:]):
        if pd.to_datetime(earlier.event_date).max()>=pd.to_datetime(later.event_date).min():
            raise ValueError('Every earlier split must precede the next split by race date.')
    return tuple(frames)


def make_model(family, alpha=None, numeric=None, categorical=None):
    numeric=NUMERIC if numeric is None else list(numeric)
    categorical=CATEGORICAL if categorical is None else list(categorical)
    if TARGET in numeric+categorical or any(name.startswith('next_') for name in numeric+categorical):
        raise ValueError('Future-known columns cannot be model inputs.')
    prepare=ColumnTransformer([
        ('numeric',Pipeline([('fill',SimpleImputer(strategy='median')),('scale',StandardScaler())]),numeric),
        ('category',Pipeline([('fill',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),categorical),
    ])
    if family=='Ridge': estimator=Ridge(alpha=float(alpha),solver='svd')
    elif family=='Lasso': estimator=Lasso(alpha=float(alpha),max_iter=100000,tol=1e-5,selection='cyclic')
    elif family=='OLS': estimator=LinearRegression()
    else: raise ValueError(f'Unknown model: {family}')
    return Pipeline([('prepare',prepare),('regression',estimator)])


def result_row(name, predictions, reference, model=None, alpha=None):
    coefficients=None if model is None else getattr(model.named_steps['regression'],'coef_',None)
    return {'model':name,'alpha':np.nan if alpha is None else alpha,
            'validation_MAE_s':float(mean_absolute_error(reference,predictions)),
            'zero_coefficients':np.nan if coefficients is None else int(np.sum(coefficients==0)),
            'coefficient_count':np.nan if coefficients is None else len(coefficients),
            'coefficient_L2_size':np.nan if coefficients is None else float(np.linalg.norm(coefficients))}


def coefficient_table(model):
    return pd.DataFrame({'encoded_input':model.named_steps['prepare'].get_feature_names_out(),
                         'coefficient':model.named_steps['regression'].coef_})


def grouped_errors(frame, predictions):
    scored=frame[['round','event_name',TARGET,'current_lap_s']].copy()
    scored['model_abs_error_s']=np.abs(scored[TARGET]-np.asarray(predictions))
    scored['persistence_abs_error_s']=np.abs(scored[TARGET]-scored.current_lap_s)
    return scored.groupby(['round','event_name']).agg(rows=(TARGET,'size'),model_MAE_s=('model_abs_error_s','mean'),persistence_MAE_s=('persistence_abs_error_s','mean')).reset_index()
