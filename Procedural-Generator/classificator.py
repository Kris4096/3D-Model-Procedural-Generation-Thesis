from pathlib import Path
import voxel
import numpy as np
import matplotlib.pyplot as plt
import utils

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Conv3D,MaxPooling3D,Dense,Dropout,Flatten
from tensorflow.keras.models import Sequential

TENSORFLOW_DATA_PATH = "tensordata/classificator_model";

    # training_data = [];
    # training_classes = [];
    # (training_data, training_classes) = glob_data("{}/train".format(path),training_data,training_classes,[1,0,0]);
    # (training_data, training_classes) = glob_data("dataset/mobile/train",training_data,training_classes,[0,1,0]);

    # training_data = np.array(training_data);
    # training_classes = np.array(training_classes);
    # print(training_classes)
    # train_classificator(training_data, training_classes)

def train_classificator():
    t_set = [];
    t_class = [];
    t_set,t_class = utils.glob_data("dataset/structureclass",t_set,t_class,[1,0,0]);
    t_set,t_class = utils.glob_data("dataset/floraclass",t_set,t_class,[0,1,0]);
    t_set,t_class = utils.glob_data("dataset/terrainclass",t_set,t_class,[0,0,1]);
    t_set = np.array(t_set);
    t_class = np.array(t_class);

    inputs = keras.Input((32,32,32,1));
    x = keras.layers.Conv3D(filters=2, kernel_size=3, activation="relu")(inputs);
    x = keras.layers.MaxPool3D(pool_size=2)(x);
    x = keras.layers.Flatten()(x);
    x = keras.layers.Dense(units=20,activation="relu")(x);
    outputs = keras.layers.Dense(units=3, activation="softmax")(x);
    model = keras.Model(inputs, outputs, name="ModelClassifier")
    
    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"]
    )

    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="logs")

    model.fit(t_set,t_class,
        epochs=20, shuffle=True, validation_split=0.2,
        callbacks=[tensorboard_callback])

    keras.utils.plot_model(model,show_shapes=True)
    model.save("tensordata/Class")
    return model

def load_classifier():
    model = keras.models.load_model("tensordata/Class")
    return model