import numpy as np
import pandas as pd
import seaborn as sns
import pytest

from app import histogram

def test_histogram():
    # Mock input values
    input.n = lambda: 100
    input.p_observed = lambda: 0.5
    input.p_0 = lambda: 0.3
    input.n_sim = lambda: 1000

    # Call the histogram function
    plot = histogram()

    # Assert the plot properties
    assert plot.get_title() == 'Steekproevenverdeling'
    assert plot.get_xlabel() == 'Steekproefproporties'
    assert plot.get_ylabel() == 'Frequentie'

    # Assert the number of bars in the histogram
    assert len(plot.patches) == 101  # 100 bins + 1 for the legend

    # Assert the color palette
    assert plot.patches[0].get_facecolor() == (0.5294117647058824, 0.807843137254902, 0.9215686274509803, 0.5)  # skyblue
    assert plot.patches[1].get_facecolor() == (0.9137254901960784, 0.5882352941176471, 0.47843137254901963, 0.5)  # salmon

    # Add more assertions as needed