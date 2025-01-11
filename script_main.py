#!/home/b/b381815/miniconda3/envs/py/bin/python
# -*- coding: utf-8 -*-

"""
(c) by Lukas Brunner (lukas.brunner@uni-hamburg.de) 2024 under a MIT License (https://mit-license.org)

Summary: Runscript to calculate a lineplot for a given day and location.
"""
import argparse
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime

from core.io import fn_base_pattern, fn_current, fn_past
from core.statistics import get_statistics
from core.lineplot import (
    plot_timeseries_base,
    plot_distribution,
    plot_mean,
    plot_year,
    plot_stats_last,
)
from core.barplot import (
    plot_histogram_base,
    plot_histogram,
)
from core.text import (
    varn_map
)
from core.utilities import (
    add_license, 
    convert_to_doy, 
    get_date_str,
    get_location_coordinates,
)


def read_input():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        dest="location",
        default="Hamburg",
        type=str,
        help="Location name",
    )

    parser.add_argument(
        "--lat",
        dest="lat",
        default=None,
        type=float,
        help="Latitude coordinate. Can be skipped if location is a AR6 region or found in database.",
    ) 

    parser.add_argument(
        "--lon",
        dest="lon",
        default=None,
        type=float,
        help="Longitude coordinate. Can be skipped if location is a AR6 region or found in database.",
    )

    parser.add_argument(
        "--year",
        dest="year",
        default=None,
        type=float,
        help="Year to plot. Defaults to the current year.",
    )

    parser.add_argument(
        "--date",
        dest="enddate",
        default=None,
        type=float,
        help="Only plot until given end date.",
    )

    parser.add_argument(
        "--startyear-base",
        dest="startyear_base",
        default=1940,
        type=int,
        help="Start year of the base period.",
    )

    parser.add_argument(
        "--endyear-base",
        dest="endyear_base",
        default=2024,
        type=int,
        help="End year of the base period.",
    )

    parser.add_argument(
        "--window-base",
        dest="window_base",
        default=1,
        type=int,
        help="Window size of the base period.",
    )

    parser.add_argument(
        "--language",
        dest="language",
        type=str,
        default="en",
        choices=["dt", "en"],
        help="Select language of plot labels.",
    )
    parser.add_argument(
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="Overwrite existing plot.",
    )

    dd = vars(parser.parse_args())
    
    if dd['lat'] is not None and dd['lon'] is not None:
        dd['location'] = {dd['location']: {'lat': dd['lat'], 'lon': dd['lon']}}
    else:
        dd['location'] = get_location_coordinates(dd['location'])
    dd.pop('lat')
    dd.pop('lon')

    return dd


def main_lineplot(
    location={'Hamburg': {'lat': 53, 'lon': 10}},
    varn='tas',
    enddate=None,  # raise Error if not in dataset?
    fn=None,
    year=None,
    language='en',

    startyear_base = 1940,
    endyear_base = 2024,
    window_base = 1,
    
    save=True,
    overwrite=False,
    show=True,
):
    if not show and not save:
        print('Either save or show need to be True')
        return None, None
        
    # --- load data to evaluate ---
    if fn is None:    
        if year is None:
            fn = fn_current
        elif '{}0101-'.format(year) in fn_current:
            fn = fn_current
        else:
            fn = fn_past
           
    da = xr.open_dataset(os.path.join(fn), use_cftime=True)[varn] 
    
    if year is not None:
        da = da.sel(time=str(year))
    elif len(np.unique(da['time.year'].values)) != 1:
        raise ValueError('More than one year of data')

    if enddate is not None:
        if isinstance(enddate, str):
            da = da.sel(time=slice(None, enddate))
        else:
            da = da.isel(time=range(0, enddate))

    if da['time'].size == 0:
        raise ValueError('No time steps selected')

    loc = list(location.keys())[0]
    date = [
        str(da['time.year'][-1].item()), 
        '{:02d}'.format(da['time.month'][-1].item()), 
        '{:02d}'.format(da['time.day'][-1].item())
    ]

    path = f'figures/{loc}/{date[0]}/{varn}/b{startyear_base}-{endyear_base}_w{window_base}/{language}/timeseries'
    os.makedirs(path, exist_ok=True)
    fullpath = os.path.join(
        path,
        'timeseries_b{startyear_base}-{endyear_base}_w{window_base}_{location}_{date}.png'.format(
            startyear_base=startyear_base, 
            endyear_base=endyear_base, 
            window_base=window_base,
            location=loc, 
            date='-'.join(date)),
    )
    if save and not show and os.path.isfile(fullpath) and not overwrite:
        return fullpath, None
    
    # --- load base distribution ---
    fn_base = fn_base_pattern.format(
        dataset='era5',
        resolution='native',
        varn=varn,
        window=window_base,
        startyear=startyear_base,
        endyear=endyear_base,
        metric='{}',
    )
    
    mean = xr.open_dataset(fn_base.format('ydrunmean'), use_cftime=True)[varn]
    std = xr.open_dataset(fn_base.format('std'), use_cftime=True)[varn]
    
    perc = xr.open_mfdataset(
        fn_base.format('p*'),
        use_cftime=True,
        combine='nested', 
        concat_dim='percentile', 
        preprocess=lambda x: x.expand_dims({'percentile': [int(x.attrs['percentile'])]})
        )[varn]
    perc = perc.sortby('percentile')
       
    perc = perc.sel(**list(location.values())[0], method='nearest').load()
    std = std.sel(**list(location.values())[0], method='nearest').load()
    mean = mean.sel(**list(location.values())[0], method='nearest').load()
    da = da.sel(**list(location.values())[0], method='nearest').load()

    if da.isel(time=0) > 100:
        mean -= 273.15
        perc -= 273.15
        da -= 273.15

    
    # delete Feb 29th for past years to be consistent with percentile calculation
    # and not have new heat records in sample, which does not make sense
    if fn == fn_past:
        da = da.convert_calendar('365_day')  

    # --- plot ---
    fig, ax = plot_timeseries_base(language=language)
    ax.set_title('{year}: {loc} {varn}'.format(
        year=date[0], 
        loc=loc,
        varn=varn_map(varn, language=language),
    ))
    fig.subplots_adjust(left=.06, right=.96, bottom=.05, top=.95)
    plot_distribution(ax, perc, labels=['Min-Max', '90%', '50%'])
    plot_mean(ax, mean)  
    add_license(ax)
    legend = ax.legend(title='{}-{}'.format(startyear_base, endyear_base))
        
    plot_year(ax, da, fill_between=mean)
    plot_stats_last(ax, da, mean, perc, std, language=language)

    info = get_statistics(da, mean, perc, std)
    info['metadata'] = {
        'varn': varn,
        'location': location,
        'date': date,
        'startyear_base': startyear_base,
        'endyear_base': endyear_base,
        'window_base': window_base,
        'language': language,
    }

    if save and (not os.path.isfile(fullpath) or overwrite):
        plt.savefig(fullpath, dpi=120)
    if not show:
        plt.close()
        
    return fullpath, info


def main_barplot(
    info: dict,
    
    save=True,
    overwrite=False,
    show=True,

    **kwargs
):
    varn = info['metadata']['varn']
    language = info['metadata']['language']
    loc = list(info['metadata']['location'].keys())[0]

        
    path = 'figures/{loc}/{year}/{varn}/b{startyear_base}-{endyear_base}_w{window_base}/{language}/histogram'.format(
        loc=loc,
        year=info['metadata']['date'][0],
        varn=varn,
        startyear_base=info['metadata']['startyear_base'],
        endyear_base=info['metadata']['endyear_base'],
        window_base=info['metadata']['window_base'],
        language=info['metadata']['language'],
    )
    os.makedirs(path, exist_ok=True)
    fullpath = os.path.join(
        path,
        'histogram_b{startyear_base}-{endyear_base}_w{window_base}_{location}_{date}.png'.format(
            startyear_base=info['metadata']['startyear_base'], 
            endyear_base=info['metadata']['endyear_base'], 
            window_base=info['metadata']['window_base'],
            location=loc,
            date='-'.join(info['metadata']['date'])))
    
    if save and not show and os.path.isfile(fullpath) and not overwrite:
        return None

    fig, ax = plot_histogram_base(
        startyear=info['metadata']['startyear_base'],
        endyear=info['metadata']['endyear_base'],
        language=info['metadata']['language'],
    )
    ax.set_title('{varn} {text} in {loc}: {text2}'.format(
        varn=varn_map(varn, True, language=language),
        text={'en': 'distribution', 'dt': 'Verteilung'}[language],
        loc=loc,
        text2={'en': '1. Jan until {}', 'dt': '1. Jan bis {}'}[language].format(get_date_str(info, "%d. %b %Y"))))
    
    bins, counts = np.unique(
        info['percentile band'],
        return_counts=True,
        axis=0,
    )
    plot_histogram(
        ax, 
        bins=bins,
        counts=counts,
    )
    add_license(ax)

    if save and (not os.path.isfile(fullpath) or overwrite):
        plt.savefig(fullpath, dpi=120)
    if not show:
        plt.close()
        
    return fullpath
    

if __name__ == '__main__':
    input_ = read_input()
    fn, info = main_lineplot(**input_)
    main_barplot(info, **input_)
    