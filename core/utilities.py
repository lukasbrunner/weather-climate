import os
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import AnnotationBbox, OffsetImage


def delete_last_day_leap_year(da: xr.DataArray) -> xr.DataArray:
    return da.where(da["dayofyear"] != 366, drop=True)


def convert_to_doy(da, delete_leap_days=True):
    if 'time' in da.dims:
        try:
            da = da.assign_coords(time=da['time.dayofyear']) 
        except AttributeError:
            pass
        da = da.rename({'time': 'dayofyear'})
    elif 'dayofyear' in da.dims:
        pass
    else:
        raise ValueError(f'Either "time" or "dayofyear" must be dimensions, found: {da.dims}')
    if delete_leap_days:
        return delete_last_day_leap_year(da)
    return da


def add_license(ax: plt.Axes) -> None:
    """Add a license to the plot."""

    arr = mpimg.imread(os.path.join('./', "by.png"))
    imagebox = OffsetImage(arr, zoom=0.15)
    ab = AnnotationBbox(
        imagebox,
        (0.01, 0.04),
        frameon=False,
        box_alignment=(0, 0),
        xycoords="axes fraction",
    )
    ax.add_artist(ab)
    ax.annotate(
        "Lukas Brunner",
        (0, 0),
        xytext=(0.01, 0.01),
        fontsize="small",
        ha="left",
        va="bottom",
        xycoords="axes fraction",
    )


def get_month_name(month: int, language='en') -> str:
    if language == 'en':
        return {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec'
        }[month]
    if language == 'de':
        return {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'Mai',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Okt',
            11: 'Nov',
            12: 'Dez'
        }[month]
    raise NotImplementedError


def get_location_coordinates(location):
    return {
        'Hamburg': {'lat': 53, 'lon': 10},
    }.get(location, {'abbrev': location})
