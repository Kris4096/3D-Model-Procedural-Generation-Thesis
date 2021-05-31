import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import utils

class Sampling(layers.Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

def train_struct_gen():
    training_data = [];
    training_data = utils.glob_only_data("dataset/structure",training_data);
    training_data = np.array(training_data);

    original_inputs = keras.Input(shape = (32,32,32,1));
    conv_filter = (2,2,2)
    pool_filter = (2,2,2)
    lval = 14
    llev = 2

    x = layers.Conv3D(48, 3, strides=1)(original_inputs)

    x = layers.Conv3D(16, 2, strides=1)(x)
    x = layers.MaxPooling3D(pool_filter)(x)
    x = layers.Conv3D(llev, 2, padding='same')(x)

    x = layers.Flatten()(x)
    x = layers.Dense(lval * lval * lval * llev, activation="relu")(x)

    z_mean = layers.Dense(lval * lval * lval * llev, name="z_mean")(x)
    z_log_var = layers.Dense(lval * lval * lval * llev, name="z_log_var")(x)
    z = Sampling()((z_mean, z_log_var))

    encoder = keras.Model(original_inputs, [z_mean, z_log_var, z], name="encoder")

    keras.utils.plot_model(encoder,to_file="model_struct_encoder.png",show_shapes=True)

    latent_inputs = keras.Input(shape=(lval*lval*lval*llev))
    x = layers.Dense(lval * lval * lval * llev, activation="relu")(latent_inputs)
    x = layers.Reshape((lval, lval, lval, llev))(x)

    x = layers.Conv3DTranspose(16, 2, strides=1)(x)
    x = layers.UpSampling3D(pool_filter)(x)
    x = layers.Conv3DTranspose(48, 3, strides=1)(x)

    reconstruction = layers.Conv3DTranspose(1, conv_filter, activation='sigmoid', padding='same')(x)
    decoder = keras.Model(latent_inputs, reconstruction, name="decoder")

    keras.utils.plot_model(decoder,to_file="model_struct_decoder.png",show_shapes=True)

    outputs = decoder(encoder(original_inputs)[2])
    vae = keras.Model(original_inputs, outputs, name='vae')

    reconstruction_loss = tf.reduce_mean(
        tf.reduce_sum(
            keras.losses.binary_crossentropy(original_inputs, outputs), axis=(1, 2, 3)
        )
    )
    kl_loss = -0.5 * (1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
    kl_loss = tf.reduce_mean(tf.reduce_sum(kl_loss, axis=1))
    total_loss = reconstruction_loss + kl_loss
    vae.add_loss(total_loss)
    vae.compile(optimizer='adam')

    vae.fit(training_data, training_data, epochs=40, shuffle=True, validation_split=0.2, batch_size=16)

    vae.summary()
    vae.save("tensordata/Struct")
    return vae

def load_struct_gen():
    model = keras.models.load_model("tensordata/Struct")
    return model