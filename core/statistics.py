import numpy as np
import xarray as xr

from core.utilities import convert_to_doy


def get_percentile_band(da, da_perc):
    """Calculates percentile band for each day of the year.

    For each day of the year (potentially from several years; untested),
    calculate the percentile exceedances. Sum over exceedances: 
    - 0 means that even the minimum was never exceeded -> new cold extreme
    - len(perc) means that even the maximum was exceeded -> new heat extreme

    Parameters
    ----------
    da : xr.DataArray, shape (N)
    da_perc : xr.DataArray (M,N)

    Return 
    ------
    shape (N,2)
    """
    da_perc = convert_to_doy(da_perc).load()
    # lower lowest bound ever so slightly to avoid new cold records in-sample
    da_perc.values[0, :] -= 1.e-5
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