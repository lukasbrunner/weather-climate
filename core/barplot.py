import numpy as np
import matplotlib.pyplot as plt

from core.statistics import get_percentile_band

def plot_histogram_base(startyear, endyear, dpi_ratio=1, language='en'):
    fig, ax = plt.subplots(
            figsize=(12 / dpi_ratio, 6 / dpi_ratio), dpi=120*dpi_ratio
    )    
    ax.set_xlim(-5, 105)
    # ax.set_ylim(0, None)

    if language == 'en':
        ax.set_xlabel('{}-{} percentile'.format(startyear, endyear))
        ax.set_ylabel('Frequency (%)')
    elif language == 'dt':
        ax.set_xlabel('{}-{} Perzentile'.format(startyear, endyear))
        ax.set_ylabel('Frequenz (%)')  
    else:
        NotImplementedError
    return fig, ax


def plot_histogram(ax, bins, counts, color='darkred', hilight_extremes='darkviolet'):

    widths = np.unique(bins[:, 1] - bins[:, 0])
    widths = widths[widths<100]
    
    if len(widths) > 1:
        raise ValueError(widths)
    else:
        width = widths[0]

    bin_edges = bins[:, 0]
    bin_edges[bin_edges==-999] = -width  
    
    ax.bar(
        bin_edges,
        counts / counts.sum() * 100,
        width=width,
        align='edge',
        color=color
    )
    
    ax.hlines(
        width,
        0, 100,
        color='k',
        ls='--',
    )    
    
    if hilight_extremes is not None:
        if 100 in bin_edges:
            ax.bar(
            100,
            counts[-1] / counts.sum() * 100,
            width=width,
            align='edge',
            color=hilight_extremes,
        )
        if -5 in bin_edges:
            ax.bar(
            -5,
            counts[0] / counts.sum() * 100,
            width=width,
            align='edge',
            color=hilight_extremes,
        )