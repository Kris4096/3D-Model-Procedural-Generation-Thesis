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

def train_terrain_tex_gen():
    input_data = [];
    training_data = [];
    combined_data = utils.glob_only_colored_data("dataset/terraintex",input_data, training_data);
    input_data = [x for x in combined_data[0]]
    input_data = np.array(input_data);
    training_data = [x for x in combined_data[1]]
    training_data = np.array(training_data);

    original_inputs = keras.Input(shape = (32,32,32,1));
    conv_filter = (4,4,4)
    pool_filter = (2,2,2)

    x = layers.Conv3D(20, conv_filter, padding='same')(original_inputs)
    x = layers.AveragePooling3D(pool_filter, padding='same')(x)

    x = layers.Conv3D(12, conv_filter, padding='same')(x)
    x = layers.AveragePooling3D(pool_filter, padding='same')(x)

    x = layers.Conv3D(6, conv_filter, padding='same')(x)
    x = layers.Flatten()(x)
    x = layers.Dense(8 *8 * 8 * 6, activation="relu")(x)

    z_mean = layers.Dense(8 * 8 * 8 * 6, name="z_mean")(x)
    z_log_var = layers.Dense(8 * 8 * 8 * 6, name="z_log_var")(x)
    z = Sampling()((z_mean, z_log_var))

    encoder = keras.Model(original_inputs, [z_mean, z_log_var, z], name="encoder")

    keras.utils.plot_model(encoder,to_file="model_terrain_tex_encoder.png",show_shapes=True)

    latent_inputs = keras.Input(shape=(8 * 8 * 8 * 6))
    x = layers.Dense(8 * 8 * 8 * 6, activation="relu")(latent_inputs)
    x = layers.Reshape((8, 8, 8, 6))(x)
    x = layers.Conv3D(6, conv_filter, padding='same')(x)

    x = layers.UpSampling3D(pool_filter)(x)
    x = layers.Conv3D(12, conv_filter, padding='same')(x)

    x = layers.UpSampling3D(pool_filter)(x)
    x = layers.Conv3D(20, conv_filter, padding='same', activation='relu')(x)

    reconstruction = layers.Conv3D(1, conv_filter, activation='sigmoid', padding='same')(x)
    decoder = keras.Model(latent_inputs, reconstruction, name="decoder")

    keras.utils.plot_model(decoder,to_file="model_terrain_tex_decoder.png",show_shapes=True)

    outputs = decoder(encoder(original_inputs)[2])
    vae = keras.Model(original_inputs, outputs, name='vae')

    #reconstruction_loss = tf.reduce_mean(
        #tf.reduce_sum(
            #keras.losses.mae(input_data, outputs), axis=(1, 2, 3)
        #)
    #)
    kl_loss = -0.5 * (1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
    kl_loss = tf.reduce_mean(tf.reduce_sum(kl_loss, axis=1))
    total_loss = kl_loss
    vae.add_loss(total_loss)
    vae.compile(optimizer='adam', loss='mse')

    vae.fit(input_data, training_data, epochs=6, shuffle=True, validation_split=0.2, batch_size=64)

    vae.summary()
    vae.save("tensordata/TerrainTex")
    return vae

def load_terrain_tex_gen():
    model = keras.models.load_model("tensordata/TerrainTex")
    return model