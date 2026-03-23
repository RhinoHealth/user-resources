import textwrap
from typing import Dict, List, Any, Optional
import numpy as np
import matplotlib.pyplot as plt
from config import COLOR_PALETTE, FIGURE_SIZE, BAR_WIDTH_FACTOR

def plot_measure_comparison(
    hospital_values: Dict[str, List[float]], 
    selected_measures: List[str], 
    n_hospitals: int, 
    title: str = "", 
    is_percentage: bool = False
) -> plt.Figure:
    """Create a grouped bar chart comparing measures across hospitals"""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    x = np.arange(len(selected_measures))
    bar_width = BAR_WIDTH_FACTOR / (n_hospitals + 1)
    
    for idx, (hospital, values) in enumerate(hospital_values.items()):
        position = x + (idx - n_hospitals/2) * bar_width
        ax.bar(position, values, bar_width, 
               label=hospital,
               color=list(COLOR_PALETTE.values())[idx % len(COLOR_PALETTE)])

    _format_plot(ax, x, selected_measures, title, is_percentage)
    return fig

def _format_plot(ax: plt.Axes, x: np.ndarray, labels: List[str], 
                title: str, is_percentage: bool) -> None:
    """Format plot axes and labels"""
    ax.set_xticks(x)
    wrapped_labels = [textwrap.fill(label, width=20) for label in labels]
    ax.set_xticklabels(wrapped_labels, rotation=45, ha="right", fontsize=10)
    
    plt.subplots_adjust(bottom=0.2)
    ax.set_ylabel(title, fontsize=12)
    if is_percentage:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    ax.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()