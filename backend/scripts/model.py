# import django
# import os
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()

import pandas as pd
import tensorflow as tf
from keras.src.utils import to_categorical
from tensorflow import keras
from keras.callbacks import EarlyStopping, ModelCheckpoint

# file = "matches_class.csv"
file = "../data/matches.csv"

FEATURES = 170
# FEATURES = 35
dataframe = pd.read_csv(file, header=None)

X_test = dataframe.sample(frac=0.1)
X_train = dataframe.drop(X_test.index)

Y_test = X_test.pop(FEATURES)
Y_train = X_train.pop(FEATURES)

# mean = X_train.mean(axis=0)
# X_train -= mean
# std = X_train.std(axis=0)
#
# X_train /= std
# X_test -= mean
# X_test /= std


model = tf.keras.models.Sequential([
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.4),
    keras.layers.Dense(1, activation='sigmoid')
])

# model = tf.keras.Sequential([
#     keras.layers.Dense(512, activation='relu'),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(512, activation='relu'),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(512, activation='relu'),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(1, activation='sigmoid')
# ])

# model = tf.keras.Sequential([
#     keras.layers.Input((FEATURES, )),
#     keras.layers.Dense(512, activation='relu',
#                        kernel_regularizer=keras.regularizers.l2(0.001),
#                        input_shape=(FEATURES,)),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(512, activation='relu',
#                        kernel_regularizer=keras.regularizers.l2(0.001)),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(512, activation='relu',
#                        kernel_regularizer=keras.regularizers.l2(0.001)),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(1, activation='sigmoid')
# ])

batch_size = 64
epochs = 4
N_TRAIN = int(1e5)
STEPS_PER_EPOCH = N_TRAIN // batch_size

model.compile(
    loss=keras.losses.BinaryCrossentropy(),
    optimizer=keras.optimizers.Adam(),
    metrics=[keras.metrics.BinaryAccuracy()]
)


# STAMP = 'simple_lstm_glove_vectors'
# early_stopping = EarlyStopping(monitor='val_loss', patience=5)
# bst_model_path = STAMP + '.h5'
# model_checkpoint = ModelCheckpoint(bst_model_path, save_best_only=True, save_weights_only=True)
# model.load_weights(bst_model_path)
# model.fit(X_train, Y_train, batch_size=batch_size,
#           epochs=epochs, validation_split=0.1, callbacks=[early_stopping, model_checkpoint])

model.fit(X_train, Y_train, batch_size=batch_size,
          epochs=epochs, validation_split=0.2, shuffle=True)

score = model.evaluate(X_test, Y_test, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])

model.save("../data/model.keras")
