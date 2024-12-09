from matplotlib.legend import Legend
from matplotlib.axes import Axes
from matplotlib.artist import Artist
from matplotlib.font_manager import FontProperties
from collections.abc import Iterable

import re
import numpy as np
from itertools import islice

from typing import Union

def __LaTeX_str_length(value: Union[str, None]) -> int:
    """
    Calculates length (in symbols) of strings with LaTeX inclusions

    Examples:
    ---------
    ::

            __LaTeX_str_length("A + $ \\chi^{2} $ + B")

    returns 10
    ::

            __LaTeX_str_length("$ \\chi^{2} $")

    returns 2

    Parameters:
    -----------
    value : str
        The string, length of which function counts
    
    Returns:
    --------
    int
    """
    if not isinstance(value, (str, type(None))):
        raise TypeError(f"TypeError: parameter ```value``` must be str or None, not {type(value)}")
    if isinstance(value, (type(None))):
        return 0
    else:
        value =  value.split('$')                                       # Splitting by $ for detecting LaTeX inclusions
        for i in range(len(value)):
            if i%2!=0:                                                  # If part of string is LaTeX inclusion
                value[i] = re.sub(r'[\{\} ]', '', value[i])
                value[i] = value[i].replace('^', ' ').replace('_', ' ')
                value[i] = re.sub(r'\\([a-zA-Z]+)', '_', value[i])
                value[i] = value[i].replace(' ', '')
        return len(''.join(value))
    
def __shifting(names : Iterable[str]=None,
               signs : Iterable[str]=None,
               values : Iterable[Union[int, float]]=None,
               errors : Iterable[Union[int, float]]=None,
               units : Iterable[str] = None,
               ROUNDING_COEF : int = 3) -> str:
    """
    Inserts delays between values in rows for pseudo-graphics

    Examples:
    ---------
    This output
    ::
        
        Altitude: [Alt] = 0.988 ± 0.001 cm
        Height: [H] = 0.326 ± 0.001 m
        Width: [Wid] = 52.322 ± 12.001 km

    could be made like this:
    ::

        Altitude: [Alt] =  0.988 ±  0.001 cm
        Height:   [H]   =  0.326 ±  0.001  m
        Width:    [Wid] = 52.322 ± 12.001 km

    Parameters:
    -----------
    names : Iterable[str]=None
        An IterAble object, which contains full names of variables,
        can be written as LaTeX text (1-st column in ex.)

    signs : Iterable[str]=None,
        An IterAble object, which contains short names of variables,
        can be written as LaTeX text (2-nd column in ex.)
    
    values : Iterable[Union[int, float]]=None,
        An IterAble object, which contains values of variables
        (3-d column in ex.)
    
    errors : Iterable[Union[int, float]]=None,
        An IterAble object, which contains errors of variables
        (4-th column in ex.)
    
    units : Iterable[str] = None
        An IterAble object, which contains units of variables
        (5-th column in ex.)
    
    ROUNDING_COEF : int = 3
        A rounding coef. which is applied to long floats before displaying
    
    Returns:
    --------
    str
    """
    LaTeX_Str_Length = np.vectorize(__LaTeX_str_length)

    # Finding maximum length in symbols in each cathegory
    Max_Length = dict(islice(locals().items(), 5))
    Row_Count = 0

    for key in Max_Length:

        if hasattr(Max_Length[key], '__iter__') and all([isinstance(i, (str, type(None))) for i in Max_Length[key]]):
            Row_Count = max(Row_Count, len(Max_Length[key]))
            Max_Length[key] = LaTeX_Str_Length(np.array(Max_Length[key])).max()

        elif hasattr(Max_Length[key], '__iter__') and all([isinstance(i, (int, float, np.float64, type(None))) for i in Max_Length[key]]):
            Row_Count = max(Row_Count, len(Max_Length[key]))
            Max_Length[key] = LaTeX_Str_Length(np.round(Max_Length[key], ROUNDING_COEF).astype(str)).max()

        elif not Max_Length[key]: 
            Max_Length[key] = 0

        else:
            raise TypeError(f"TypeError: ```{key}``` argument must contain elements of one type")
        
    # Shifting
    Parts = dict(islice(locals().items(), 5))
    for key in Parts:
        if Parts[key]:
            for row in range(Row_Count):
                if key=='names':
                    if Parts[key][row]: Parts[key][row] += ' '*int(Max_Length[key]-__LaTeX_str_length(Parts[key][row]))
                    else: Parts[key][row] = ' '*int(Max_Length[key])
                if key=='signs':
                    if Parts[key][row]: Parts[key][row] = '['+Parts[key][row]+']'+' '*int(Max_Length[key]-__LaTeX_str_length(Parts[key][row]))
                    else: Parts[key][row] = ' '*int(Max_Length[key]+2)
                if key=='values' or key=='errors':
                    if Parts[key][row]: Parts[key][row] = ' '*int(Max_Length[key]-__LaTeX_str_length(str(round(Parts[key][row], ROUNDING_COEF))))+str(round(Parts[key][row], ROUNDING_COEF))
                    else: Parts[key][row] = ' '*int(Max_Length[key])
                if key=='units':
                    if Parts[key][row]: Parts[key][row] = ' '*int(Max_Length[key]-__LaTeX_str_length(Parts[key][row]))+Parts[key][row]
                    else: Parts[key][row] = ' '*int(Max_Length[key])

    # Concatenating result
    Result = ['']*Row_Count
    for row in range(Row_Count):
        if Parts['names'][row].replace(' ', '')=='': Result[row] += Parts['names'][row]+' '*2
        else: Result[row] += Parts['names'][row] + ': '
        
        if Parts['signs'][row].replace(' ', '')=='': Result[row] += Parts['signs'][row]+' ='
        else: Result[row] += Parts['signs'][row] + ' ='

        if Parts['values'][row].replace(' ', '')=='': Result[row] += ' '+Parts['values'][row]+' ± '
        else: Result[row] += ' '+Parts['values'][row]+' ± '

        if Parts['errors'][row].replace(' ', '')=='': Result[row] += ' '+Parts['errors'][row]+' '
        else: Result[row] += ' '+Parts['errors'][row]+' '

        if Parts['units'][row].replace(' ', '')=='': Result[row] += ' '+Parts['units'][row]
        else: Result[row] += ' '+Parts['units'][row]

    return '\n'.join(Result)

def Metrix_legend(ax : Axes,
                  handles : Iterable[Artist],
                  Y_obs : Iterable[Iterable[Union[int, float]]],
                  Y_pred : Iterable[Iterable[Union[int, float]]],
                  R2 : Iterable[bool] = None,
                  chi : Iterable[bool] = None,
                  RMSE : Iterable[bool] = None,
                  ROUNDING_COEF : int = 3,
                  title_fontproperties : FontProperties = None,
                  title : str = "Metrics:",
                  prop : FontProperties = None,
                  loc : str = 'best',
                  labelspacing : Union[int, float] = 0.7,
                  handletextpad : Union[int, float] = 0.1,
                  draggable : bool = True,
                  bbox_to_anchor : tuple = None) -> Legend:
    if not ax:
        raise ValueError("ValueError: parameter ```ax``` must not be None")
    if not handles:
        raise ValueError("ValueError: parameter ```handles``` must not be None")
    
    SAMPLES_NUM = len(handles)

    if not SAMPLES_NUM==len(Y_obs)==len(Y_pred):
        raise ValueError(f"ValueError: ```handles, Y_obs, Y_pred``` must have same number of samples, not [{SAMPLES_NUM}, {len(Y_obs)}, {len(Y_pred)}]")
        
    if not R2 or chi or RMSE: 
        R2 = [True]*SAMPLES_NUM
        chi = [True]*SAMPLES_NUM
        RMSE = [True]*SAMPLES_NUM
    else: 
        if not len(R2)==len(chi)==len(RMSE)==SAMPLES_NUM:
            raise ValueError(f"ValueError: parameters ```handles, R2, chi, RMSE``` must have same number of samples, not [{SAMPLES_NUM}, {len(R2)}, {len(chi)}, {len(RMSE)}]")

    if not title_fontproperties: title_fontproperties = FontProperties(family='monospace', size=10, weight='normal', style='normal')
    if not prop: prop = FontProperties(family='monospace', size=10, weight='normal', style='normal')

    # for handle in :

    # return ax.legend(handles=handles,
    #                  labels=
    #                  title_fontproperties=title_fontproperties,
    #                  title=title, prop=prop,
    #                  loc=loc, labelspacing=labelspacing, handletextpad=handletextpad, draggable=draggable, bbox_to_anchor=bbox_to_anchor)
    return ax.legend()