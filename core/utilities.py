import os
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from glob import glob
from datetime import datetime


def get_datetime(info):
    return datetime.strptime('-'.join(info['metadata']['date']), '%Y-%m-%d')


def get_date_str(info, format_='%a %d. %b %Y', language=None):
    if language is None:
        language = info['metadata']['language']
    ss = datetime.strftime(get_datetime(info), format_)
    if language == 'en':
        return ss
    if language == 'dt':
        return ss.replace(
            'May', 'Mai').replace(
            'Oct', 'Okt').replace(
            'Dec', 'Dez').replace(
            'Mon', 'Mo').replace(
            'Tue', 'Di').replace(
            'Wed', 'Mi').replace(
            'Thu', 'Do').replace(
            'Fri', 'Fr').replace(
            'Sat', 'Sa').replace(
            'Sun', 'So')
    

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

    arr = mpimg.imread(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 
        '..',
        "by.png"
    ))
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



def get_location_coordinates(location):
    return {location: {
        'Hamburg': {'lat': 53, 'lon': 10},
        'Vienna': {'lat': 48.2, 'lon': 16.3},
        'Zurich': {'lat': 47.3, 'lon': 8.5},
        'Edinburgh': {'lat': 56.0, 'lon': 360 - 3.2},
        'Osaka': {'lat': 34.6, 'lon': 135.5},
        'San Francisco': {'lat': 37.8, 'lon': 360 - 122.5},
        'Casablanca': {'lat': 33.5, 'lon': 360 - 7.5},
    }.get(location, {'abbrev': location})}



def get_image_filenames(
    location='Hamburg', 
    year=2024, 
    startyear_base=1940,
    endyear_base=2023,
    window_base=1,
    check_complete=False,
):
    if check_complete:
        pass
    else:
        return sorted(glob(os.path.join(
            'figures',
            location,
            str(year),
            'b{}-{}_w{}'.format(
                startyear_base, 
                endyear_base,
                window_base),
            '*.png')))


def get_image_file(
    location='Hamburg', 
    year=2024, 
    startyear_base=1940,
    endyear_base=2023,
    window_base=1,
    check_complete=False,
    date='last',
):
    filenames = get_image_filenames(
        location=location, 
        year=year, 
        startyear_base=startyear_base,
        endyear_base=endyear_base,
        window_base=window_base,
        check_complete=check_complete,
    )
    if date == 'last':
        return filenames[-1]
    return (fn for fn in filenames if date in fn)



def combine_to_gif(
    fn_last: str,
    delay: int = 10,
    max_duration=5,
    resize: int = 1000,
    overwrite=True,
    loop=False,
):
    """Combine individual figures to gif.

    Parameters
    ----------
    fn : str
        full path (path + filename + extension) of the last figure (will determine
        gif filename)
    stepsize : int, by default 'auto'
        If auto the stepsize will be chosen so that the gif has max 100 steps.
        Set to 1 to include all figures (might result in large file sizes).
    delay : int, by default 10
        In 1/100 seconds. See convert -h delay
    max_duration: int, by default 5
        Maximum duration of the animation in seconds. Overwrites delay.
        Delay is limited to [1, 50]
    resize : int, by default 640
        See convert -h resize
    """
    path, fn = os.path.split(fn_last)
    fn, ext = os.path.splitext(fn)
    path_parent = "/".join(path.split("/")[:-1])

    filenames = sorted(glob(os.path.join(path, f"*{ext}")))
    if max_duration is not None:
        delay = min([max([5, int(max_duration* 100 / len(filenames))]), 50])

    fn += f"_d{delay}_s{resize}"
    fn = os.path.join(path_parent, fn + ".gif")

    filenames = " ".join(filenames)

    if overwrite or not os.path.isfile(fn):
        if loop: 
            os.system(f"module load clint freva; convert -delay {delay} -resize {resize} {filenames} {fn}")
        else:
            os.system(f"module load clint freva; convert -delay {delay} -resize {resize} -loop 1 {filenames} {fn}")

    return fn