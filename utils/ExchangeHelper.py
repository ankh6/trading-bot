from typing import List
from errors.Exceptions import LabelNotFoundError
import pandas as pd

def convert_object_to_string(input) -> object:
    ''' Converts an input of type object to an input of type string
    
    Arguments:
    input, the input to be converted

    Return:
    input: the converted input
    '''
    return str(input)

def convert_object_series_to_datetime(source_dataframe: pd.DataFrame, timestamp_labels: List[str]):
    ''' Converts a pandas series of unix epoch milliseconds (timestamps) values into a series of datetime values
        
    By the default the function updates inplace the original DataFrame
    This function facilitates the handling of time-series values
    
    Arguments:
    source_dataframe: the pandas DataFrame that exposes the labels to be converted
    timestamp_labels: a list of label/column names 
    '''
    for single_label in timestamp_labels:
        try:
            source_dataframe[single_label].apply(convert_object_to_string, convert_dtype=False)
            source_dataframe[single_label] = pd.to_datetime(source_dataframe[single_label], dayfirst=False, yearfirst=True, unit="ms", origin="unix", utc=True)
        except KeyError:
            raise LabelNotFoundError(f"Please provide a label that is expose by the dataframe\nProvided labels: {timestamp_labels}")
        except Exception as e:
            print(e.args)
            raise e