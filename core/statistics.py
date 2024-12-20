import numpy as np
import xarray as xr

from core.utilities import convert_to_doy


def get_percentile_band(da, da_perc):
    da_perc = convert_to_doy(da_perc)
    return xr.apply_ufunc(
        lambda pp: np.array([
            da_perc['percentile'][pp-1].item() if pp > 0 else -999, 
            da_perc['percentile'][pp].item() if pp < da_perc['percentile'].size else 999]),
        (da.groupby('time.dayofyear') > da_perc.load()).sum('percentile'),
        output_core_dims=[['bounds']],
        vectorize=True,
    )


def get_statistics(da, da_mean, da_perc, da_std):
    da_mean = convert_to_doy(da_mean)
    da_perc = convert_to_doy(da_perc)
    da_std = convert_to_doy(da_std)
    
    return {
        'difference to mean': da.groupby('time.dayofyear') - da_mean,
        'standard deviations to mean': (da.groupby('time.dayofyear') - da_mean).groupby('time.dayofyear') / da_std,
        'percentile band': get_percentile_band(da, da_perc),
    }