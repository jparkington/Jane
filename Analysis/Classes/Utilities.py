'''
Author: James Parkington
Date:   2023-03-31
Module: Utilities

This utility module provides functions for generating data, converting it into a pandas DataFrame, saving it to a CSV file, and constructing file paths.
It also contains a function to load the ipython-sql extension and establish a connection to a SQLite database.
It is meant to be used by other classes or scripts that require similar functionality.

Functions:
    save_path: Constructs a file path based on the provided subdirectories and an optional parent directory inclusion
    to_dataframe: Converts the generated data to a pandas DataFrame, sorts it, and optionally saves it to a SQLite database table and/or a CSV file
    load_sql: Loads the ipython-sql extension and establishes a connection to a SQLite database
    load_plot: Applies a custom dark style and common customizations to a pyplot visualization and returns the pyplot, Axes, and color palette objects
    polynomial_regression: Performs polynomial regression and returns the forecast dates and forecasted values
    get_state_name: Converts a two-letter state code to its full state name using the state_dict dictionary
'''

from IPython               import get_ipython
from sklearn.linear_model  import Ridge
from sklearn.preprocessing import PolynomialFeatures

import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import os
import sqlite3
import seaborn

def save_path(use_parent_directory, 
              *subdirs):
    '''
    Construct a file path based on the provided subdirectories.
    Optionally, include the parent directory in the path.

    Args:
        use_parent_directory (bool): If True, include the parent directory in the path.
        subdirs (str): Subdirectories to include in the path.

    Returns:
        str: The constructed file path.
    '''
    if use_parent_directory:
        path = os.path.join('..', *subdirs)
    else:
        path = os.path.join(*subdirs)

    return path


def to_dataframe(data, 
                 by        = None, 
                 ascending = True,
                 add_id    = True, 
                 filename  = None,
                 sql_table = None):
    '''
    Return a pandas DataFrame representation of the data dictionary object.
    Optionally save the DataFrame to a CSV file if the filename is provided.

    Args:
        data (dict): The data to be converted to a DataFrame.
        by (str or list of str, optional): Column(s) to sort the DataFrame by.
        ascending (bool, optional): Sort order for the specified columns. Defaults to True.
        filename (str, optional): Name of the CSV file to save the DataFrame to.
        sql_table (str, optional): Name of the SQL table to save the DataFrame to.

    Returns:
        pd.DataFrame: The sorted DataFrame with an id column added.
    
    Considerations:
        An id column is added with monotonically increasing integers starting from 1 to facilitate record identification and improve query performance.
        If ascending is skipped, the function will apply the default True to all columns in the by argument
    '''
    df = pd.DataFrame(data)
    if by:
        df = df.sort_values(by        = by, 
                            ascending = ascending)

    if add_id:
        df.insert(0, 'id', range(1, len(df) + 1))

    if filename:
        df.to_csv(filename, index = False)

    if sql_table:
        df.to_sql(sql_table, 
                  sqlite3.connect(save_path(True, 'Data', 'jane.db')),
                  if_exists = 'replace', 
                  index     = False)
        
    return df


def load_sql():
    '''
    Load the ipython-sql extension and establish a connection to the SQLite database.
    
    This function is designed to be used in Jupyter Notebooks. It loads the ipython-sql extension and connects to the SQLite database using the provided file path.
    '''
    ipy = get_ipython()
    
    # Check if the 'sql' extension is already loaded
    if not ipy.find_line_magic("sql"):
        ipy.run_line_magic("load_ext", "sql")
        
    ipy.run_line_magic("sql", f"sqlite:///{save_path(True, 'Data', 'jane.db')}")


def load_plot(figsize = (10, 6)):
    """
    Apply a custom dark style and common customizations to a pyplot visualization
    and return the pyplot, Axes, and color palette objects.

    Args:
        figsize (tuple, optional): The width and height of the figure in inches. Defaults to (10, 6).

    Returns:
        matplotlib.pyplot:     The pyplot object.
        matplotlib.axes.Axes:  The customized axes object.
        seaborn.color_palette: The color palette.
    """
    plt.style.use(['seaborn-v0_8-darkgrid'])
    plt.rcParams.update({"figure.facecolor"      : "0.116",
                         "axes.titlecolor"       : "1",
                         "axes.labelcolor"       : "1",
                         "xtick.color"           : "1",
                         "ytick.color"           : "1",
                         "xtick.labelsize"       : 8,
                         "ytick.labelsize"       : 8,
                         "grid.linestyle"        : ":",
                         "font.family"           : "DejaVu Sans Mono", 
                         "axes.titleweight"      : "bold",
                         "axes.labelweight"      : "bold",
                         "figure.figsize"        : figsize,
                         "legend.loc"            : "upper right",
                         "legend.fontsize"       : 8,
                         "legend.title_fontsize" : 10})
    
    _, ax = plt.subplots()
    ax.spines[:].set_visible(False)
    plt.tight_layout()

    return plt, ax, seaborn.color_palette('Set2') + seaborn.color_palette('husl')

def polynomial_regression(x, 
                          y, 
                          degree = 2, 
                          days   = 20, 
                          alpha  = 500):
    """
    Perform polynomial regression and return the forecast dates and forecasted values.

    Args:
        x (array-like):          The input values for the regression.
        y (array-like):          The output values for the regression.
        degree (int, optional):  The degree of the polynomial. Defaults to 2.
        days(int, optional):     The number of days to predict. Defaults to 20.
        alpha (float, optional): The regularization strength for the Ridge model. Defaults to 500.

    Returns:
        tuple: A tuple containing the forecast dates (numpy array) and forecasted values (numpy array).

    Considerations:
        The default values for degree, days_to_predict, and alpha are set according to the specific problem being solved.
        Adjusting these values may be necessary depending on the nature of the data and the desired level of model complexity.
    """
    origin   = pd.Timestamp(x.min())
    x_series = (pd.Series(x).apply(pd.Timestamp) - origin).dt.days.values.reshape(-1, 1)
    features = PolynomialFeatures(degree)
    dates    = np.arange(x_series.max() + 1, x_series.max() + 1 + days).reshape(-1, 1)
    
    return origin + pd.to_timedelta(dates.flatten(), unit = 'D'), \
           Ridge(alpha).fit(features.fit_transform(x_series), y.values).predict(features.transform(dates))

def get_state_name(state_abbr):
    '''
    Convert a two-letter state code to its full state name using the state_dict dictionary.

    Args:
        state_abbr (str): The two-letter state code.

    Returns:
        str: The full state name, or None if the state code is not found in the dictionary.
    '''

    state_dict = {'AL': 'Alabama',        'AK': 'Alaska',        'AZ': 'Arizona', 
                  'AR': 'Arkansas',       'CA': 'California',    'CO': 'Colorado',
                  'CT': 'Connecticut',    'DE': 'Delaware',      'FL': 'Florida', 
                  'GA': 'Georgia',        'HI': 'Hawaii',        'ID': 'Idaho',
                  'IL': 'Illinois',       'IN': 'Indiana',       'IA': 'Iowa', 
                  'KS': 'Kansas',         'KY': 'Kentucky',      'LA': 'Louisiana',
                  'ME': 'Maine',          'MD': 'Maryland',      'MA': 'Massachusetts', 
                  'MI': 'Michigan',       'MN': 'Minnesota',     'MS': 'Mississippi',
                  'MO': 'Missouri',       'MT': 'Montana',       'NE': 'Nebraska', 
                  'NV': 'Nevada',         'NH': 'New Hampshire', 'NJ': 'New Jersey',
                  'NM': 'New Mexico',     'NY': 'New York',      'NC': 'North Carolina', 
                  'ND': 'North Dakota',   'OH': 'Ohio',          'OK': 'Oklahoma',
                  'OR': 'Oregon',         'PA': 'Pennsylvania',  'RI': 'Rhode Island',
                  'SC': 'South Carolina', 'SD': 'South Dakota',  'TN': 'Tennessee',
                  'TX': 'Texas',          'UT': 'Utah',          'VT': 'Vermont', 
                  'VA': 'Virginia',       'WA': 'Washington',    'WV': 'West Virginia', 
                  'WI': 'Wisconsin',      'WY': 'Wyoming'}
    
    return state_dict.get(state_abbr.upper(), None)
