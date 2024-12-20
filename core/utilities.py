import os
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from glob import glob
from datetime import datetime


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


def get_default_text(info):
    return '\n'.join([
    'Maximum temperature in {} until {}'.format(
        list(info['metadata']['location'])[0],
        # info['difference to mean'][-1].time.dt.strftime("%a %-d. %b %Y").item()),
        datetime.strftime(datetime.strptime('-'.join(info['metadata']['date']), '%Y-%m-%d'), "%a %-d. %b %Y")),
    'Maximum temperature anomaly in {} so far: {:.1f}°C'.format(
        info['difference to mean']['time.year'][-1].item(),
        info['difference to mean'].mean('time').item())
])


def get_image_alt(info):
    date = datetime.strftime(
        datetime.strptime('-'.join(info['metadata']['date']), '%Y-%m-%d'), "%a %-d. %b %Y")
    return ' '.join([
        'A figure showing the temperature evolution in {location} in {year}.',
        'Gray in the background is the {startyear_base}-{endyear_base} distribution,',
        'red in the foreground the temperature for {year}.',
        'The most recent date shown is {date}, it has an anomaly',
        'to the mean of the baseline of {anom:+.1f}°C or {anom_std:+.1f} standard deviations.'
    ]).format(
        location=list(info['metadata']['location'])[0],
        year=info['metadata']['date'][0],
        startyear_base=info['metadata']['startyear_base'],
        endyear_base=info['metadata']['endyear_base'],
        date=date,
        anom=info['difference to mean'][-1].item(),
        anom_std=info['standard deviations to mean'][-1].item(),
    )
    

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


import os
from glob import glob


def combine_to_gif(
    fn_last: str,
    delay: int = 10,
    max_duration=5,
    resize: int = 1000,
    overwrite=True,
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
    resize : int, by default 640
        See convert -h resize
    """
    path, fn = os.path.split(fn_last)
    fn, ext = os.path.splitext(fn)
    path_parent = "/".join(path.split("/")[:-1])

    filenames = sorted(glob(os.path.join(path, f"*{ext}")))
    if max_duration is not None:
        delay = min([max([1, int(max_duration* 100 / len(filenames))]), 50])

    fn += f"_d{delay}_s{resize}"
    fn = os.path.join(path_parent, fn + ".gif")

    filenames = " ".join(filenames)

    if overwrite or not os.path.isfile(fn):
        os.system(f"module load clint freva; convert -delay {delay} -resize {resize} -loop 1 {filenames} {fn}")