import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import tensorflow as tf
from tensorflow import keras

from catvsdog_model.config.core import config
from catvsdog_model.processing.features import data_augmentation


# Create a function that returns a model
def create_model(input_shape, optimizer, loss, metrics):

    inputs = keras.Input(shape=input_shape)
    x = data_augmentation(inputs)
    x = keras.layers.Rescaling(1. / config.model_config.scaling_factor)(x)
    x = keras.layers.Conv2D(filters=32, kernel_size=3, activation="relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=2)(x)
    x = keras.layers.Conv2D(filters=64, kernel_size=3, activation="relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=2)(x)
    x = keras.layers.Conv2D(filters=128, kernel_size=3, activation="relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=2)(x)
    x = keras.layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
    x = keras.layers.MaxPooling2D(pool_size=2)(x)
    x = keras.layers.Conv2D(filters=256, kernel_size=3, activation="relu")(x)
    
    x = keras.layers.Flatten()(x)
    x = keras.layers.Dropout(0.5)(x)
    outputs = keras.layers.Dense(1, activation="sigmoid")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    return model


# Create model
classifier = create_model(input_shape = config.model_config.input_shape, 
                          optimizer = config.model_config.optimizer, 
                          loss = config.model_config.loss, 
                          metrics = [config.model_config.accuracy_metric])
