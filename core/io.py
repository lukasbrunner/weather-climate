import os

basepath = '/work/uc1275/LukasBrunner/bluesky_bot'

path_base_pattern = 'base_distributions/{dataset}_{resolution}_b{startyear}-{endyear}_w{window}'
fn_base_pattern = '{varn}_day_{dataset}_b{startyear}-{endyear}_w{window}_{metric}.nc'
fn_base_pattern = os.path.join(basepath, path_base_pattern, fn_base_pattern)

fn_past = os.path.join(basepath, 'raw_data', 'tas_day_era5.nc')
fn_current = os.path.join(basepath, 'raw_data', 'tas_day_reanalysis_era5_r1i1p1_20250101-20251231.nc')
