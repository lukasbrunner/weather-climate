import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from core.utilities import convert_to_doy, get_month_name


def plot_timeseries_base(location, dpi_ratio=1, language='en'):
    fig, ax = plt.subplots(
            figsize=(12 / dpi_ratio, 6 / dpi_ratio), dpi=120*dpi_ratio
    )
    ax.set_xlim(1, 365)
    ax.set_xticks([1, 60, 121, 182, 243, 304, 365])

    if language == 'en':
        ax.set_ylabel("Temperature ($^\\circ$C)")
        ax.set_xticklabels(["1. Jan.", "1. Mar.", "1. May", "1. Jul.", "1. Sep", "1. Nov.", "31. Dec."])
        ax.set_title(f'{location} daily maximum temperature')
    elif language == 'de':
        ax.set_ylabel("Temperatur ($^\\circ$C)")
        ax.set_xticklabels(["1. Jän.", "1. März", "1. Mai", "1. Jul.", "1. Sep", "1. Nov.", "31. Dez."])
        ax.set_title(f'Tägliche Maximaltemperatur in {location}')
    else:
        NotImplementedError
        
    return fig, ax
      

def plot_mean(ax, da, label='Mean'):
    da = convert_to_doy(da)
    ax.plot(
        da['dayofyear'],
        da,
        color='k',
        label=label,
    )
    

def plot_distribution(ax, da, percentiles=[(0, 100), (5, 95), (25, 75)], labels='auto'):
    da = convert_to_doy(da)   
    
    for idx, pp in enumerate(percentiles):
        ax.fill_between(
            da['dayofyear'],
            da.sel(percentile=pp[0]),
            da.sel(percentile=pp[1]),
            facecolor='k',
            edgecolor='none',
            alpha=.1#1/(len(percentiles) + 2),
        )
        if labels is not None:
            if labels == 'auto':
                labels = ['{}-{}'.format(pp[0], pp[1]) for pp in percentiles]
            ax.fill_between(
                [], [], [],
                facecolor='k', edgecolor='none',
                alpha=.1*(idx+1),
                label=labels[idx],
            )

    
def plot_year(ax, da, color='darkred', label=None, highlight_last=True, fill_between=None):
    da = convert_to_doy(da)
    
    ax.plot(
        da['dayofyear'],
        da,
        color=color,
        label=label,
    )

    if highlight_last:
        ax.scatter(
            da['dayofyear'][-1],
            da[-1],
            color=color,
            s=10,
        )

    if fill_between is not None:
        ref = convert_to_doy(fill_between)
        ax.fill_between(
            da['dayofyear'],
            da,
            ref.sel(dayofyear=da['dayofyear']),
            where=da > ref.sel(dayofyear=da['dayofyear']),
            color='darkred',
            alpha=.2,
        )
        ax.fill_between(
            da['dayofyear'],
            da,
            ref.sel(dayofyear=da['dayofyear']),
            where=da < ref.sel(dayofyear=da['dayofyear']),
            color='darkblue',
            alpha=.2,
        )
            


def plot_stats_last(ax, da, da_mean, da_perc, da_std, color='darkred', language='en'):
    date_last = '{:02d}. {}'.format(
        da['time.day'][-1].item(), 
        get_month_name(da['time.month'][-1].item(), language=language),
        # da['time.year'][-1].item(),
    )
    
    da = convert_to_doy(da)
    da_mean = convert_to_doy(da_mean)
    da_perc = convert_to_doy(da_perc)
    da_std = convert_to_doy(da_std)
    
    doy_last = da['dayofyear'][-1].item()
    
    da_last = da.sel(dayofyear=doy_last).item()
    da_mean_last = da_mean.sel(dayofyear=doy_last).item()
    da_std_last = da_std.sel(dayofyear=doy_last).item()
    anom = da_last - da_mean_last
    anom_std = anom / da_std_last
    text = f"{date_last}\n{anom:+.1f}$^\\circ$C\n{anom_std:+.1f} SD"
    
    
    ax.vlines(doy_last, da_last, da_mean_last, colors=color, ls=":", lw=1)

    xx = np.min([doy_last + 5, 340])
    yy = da_last - anom / 2
    va = 'center'
    if doy_last > 335:
        if anom < 0:
            yy = da.sel(dayofyear=slice(330, None)).min() - 1
            va = 'top' 
        else:
            yy = da.sel(dayofyear=slice(330, None)).max() + 1
            va = 'bottom'        

    ax.text(
        xx,
        yy,
        text,
        color=color,
        ha='left',
        va=va,
        multialignment="left",
        bbox=dict(facecolor="w", alpha=0.6, edgecolor="none"),
    )

