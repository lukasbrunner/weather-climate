import numpy as np
import matplotlib.pyplot as plt

from core.statistics import get_percentile_band


def plot_histogram_base(startyear, endyear, language='en'):
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    ax.set_xlim(-5, 105)
    # ax.set_ylim(0, None)

    if language == 'en':
        ax.set_xlabel('{}-{} percentile'.format(startyear, endyear))
        ax.set_ylabel('Frequency (%)')
    elif language == 'de':
        ax.set_xlabel('{}-{} Perzentile'.format(startyear, endyear))
        ax.set_ylabel('Frequenz (%)')     
    else:
        NotImplementedError
    return fig, ax


def plot_histogram(ax, da, da_perc, color='darkred', highlight_last=True):
    bins, counts = np.unique(
        get_percentile_band(da, da_perc).values, 
        axis=0, return_counts=True,
    )
    width = bins[1, 1] - bins[1, 0]
    
    ax.bar(
        bins[:, 0],
        counts / counts.sum() * 100,
        width=width,
        align='edge',
        color=color
    )
    
    ax.hlines(
        1 / (len(bins)-2) * 100,
        0, 100,
        color='k',
        ls='--',
    )

    if highlight_last:
        xx = get_percentile_band(da, da_perc).isel(time=[-1]).values[0, 0]
        ax.scatter(
            xx + width / 2,
            (counts[np.where(bins[:, 0] == xx)[0]] + 1) / counts.sum() * 100,
            facecolor='darkred',
            edgecolor='none',
            s=50,
            marker='*' if (xx > 100) or (xx < 0) else '.',
        )