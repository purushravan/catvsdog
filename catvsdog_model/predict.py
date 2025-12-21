import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from typing import Union
import pandas as pd
import tensorflow as tf

from catvsdog_model import __version__ as _version
from catvsdog_model.config.core import config
from catvsdog_model.processing.data_manager import load_model, load_test_dataset

model_file_name = f"{config.app_config.model_save_file}{_version}"
clf_model = load_model(file_name = model_file_name)


def make_prediction(*, input_data: Union[pd.DataFrame, dict, tf.Tensor]) -> dict:
    """Make a prediction using a saved model """
    
    results = {"predictions": None, "version": _version}
    
    predictions = clf_model.predict(input_data, verbose = 0)
    pred_labels = []
    for i in predictions:
        pred_labels.append(config.model_config.label_mappings[int(predictions + 0.5)])
        
    results = {"predictions": pred_labels, "version": _version}
    print(results)

    return results


if __name__ == "__main__":

    test_data = load_test_dataset()
    for data, labels in test_data:
        data_in = data[0]
        break
    
    data_in = tf.reshape(data_in, (1, 180, 180, 3))
    make_prediction(input_data = data_in)