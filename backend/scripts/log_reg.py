import pandas as pd
from matplotlib import pyplot as plt
from sklearn import linear_model, metrics
import pandas as pd
# import tensorflow as tf
# from keras.src.utils import to_categorical
# from tensorflow import keras
# from keras.callbacks import EarlyStopping, ModelCheckpoint

file = "../data/stomp.csv"

FEATURES = 4
# FEATURES = 35
dataframe = pd.read_csv(file, header=None)

X_test = dataframe.sample(frac=0.2, random_state=123)
X_train = dataframe.drop(X_test.index)
print(X_test.head())
Y_test = X_test.pop(FEATURES)
Y_train = X_train.pop(FEATURES)

reg = linear_model.LogisticRegression()

reg.fit(X_train, Y_train)

y_pred = reg.predict(X_test)
print("Logistic Regression model accuracy(in %):",
      metrics.accuracy_score(Y_test, y_pred) * 100)

proba = reg.predict_proba(X_test)
data = [prob[0] for prob in proba]

plt.hist(data, bins=50)
plt.savefig("new_plots")
# model = tf.keras.models.Sequential([
#     keras.layers.Dense(64, activation='relu'),
#     keras.layers.Dense(32, activation='relu'),
#     keras.layers.Dropout(0.5),
#     keras.layers.Dense(1, activation='sigmoid')
# ])
#
# batch_size = 32
# epochs = 50
# N_TRAIN = int(1e5)
# STEPS_PER_EPOCH = N_TRAIN // batch_size
#
# model.compile(
#     loss=keras.losses.BinaryCrossentropy(),
#     optimizer=keras.optimizers.Adam(),
#     metrics=['binary_accuracy']
# )
#
# model.fit(X_train, Y_train, batch_size=batch_size,
#           epochs=epochs, validation_split=0.1)
#
# score = model.evaluate(X_test, Y_test, verbose=0)
# print("Test loss:", score[0])
# print("Test accuracy:", score[1])