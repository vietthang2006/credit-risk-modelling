import numpy as np
import pandas as pd
from pathlib import Path

def reduce_mem_usage(data: pd.DataFrame, verbose=True):
    start_mem = data.memory_usage(deep=True).sum() / 1024 * 2

    if verbose:
        print('_' * 100)
        print(f'Memory usage of DataFrame: {start_mem:.2f}')

    for col in data.columns:
        col_type = data[col].dtype

        # String -> category
        if pd.api.types.is_string_dtype(col_type):
            data[col] = data[col].astype('category')

        # Integer
        elif pd.api.types.is_integer_dtype(col_type):
            c_min = data[col].min()
            c_max = data[col].max()

            if c_min >= 0:
                if c_max <= np.iinfo(np.uint8).max:
                    data[col] = data[col].astype(np.uint8)
                elif c_max <= np.iinfo(np.uint16).max:
                    data[col] = data[col].astype(np.uint16)
                elif c_max <= np.iinfo(np.uint32).max:
                    data[col] = data[col].astype(np.uint32)
                else:
                    data[col] = data[col].astype(np.uint64)

            else:
                if c_min >= np.iinfo(np.int8).min and c_max <= np.iinfo(np.int8).max:
                    data[col] = data[col].astype(np.int8)
                elif c_min >= np.iinfo(np.int16).min and c_max <= np.iinfo(np.int16).max:
                    data[col] = data[col].astype(np.int16)
                elif c_min >= np.iinfo(np.int32).min and c_max <= np.iinfo(np.int32).max:
                    data[col] = data[col].astype(np.int32)
                else:
                    data[col] = data[col].astype(np.int64)

        # Float
        elif pd.api.types.is_float_dtype(col_type):
            data[col] = data[col].astype(np.float32)

    end_mem = data.memory_usage(deep=True).sum() / 1024 * 2
    if verbose:
        print(f'Memory usage after reducing: {end_mem:.2f}')
        print(f'Decreased by {(start_mem - end_mem) / start_mem:.1%}')
    return data

def restore_parquet(data: pd.DataFrame, filename: str):
    PROCESSED_DIR = Path("./Home Credit Dataset/interim/modelling")
    output_path = PROCESSED_DIR / f'{filename}.parquet'
    data.to_parquet(
        output_path,
        engine='pyarrow',
        index=False
    )
    return output_path
    