# A small module that customizes Altair plots
import pandas as pd
import os.path as op
import os
from glob import glob

def alt_theme():
    return {
        'config': {
            'axisLeft': {
                'labelFontSize': 15,
            },
            'axisBottom': {
                'labelFontSize': 15,
            },
        }
    }