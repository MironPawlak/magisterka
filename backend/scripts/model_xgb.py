import django
import os

from matplotlib import pyplot as plt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import pandas as pd
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier

from apps.matches.management.commands.create_csv import translate_champions

# file = "matches_class.csv"
file = "../data/matches.csv"
# FEATURES = 70
FEATURES = 169
dataframe = pd.read_csv(file, header=None)

X_test = dataframe.sample(frac=0.1, random_state=123)
X_train = dataframe.drop(X_test.index)

Y_test = X_test.pop(FEATURES)
Y_train = X_train.pop(FEATURES)

print(Y_train)
plt.hist(Y_train, bins=50)
plt.savefig("plots")

# model = XGBClassifier()
# model.fit(X_train, Y_train)
# y_pred = model.predict(X_test)
# predictions = [round(value) for value in y_pred]
# accuracy = accuracy_score(Y_test, predictions)
# print("Accuracy: %.2f%%" % (accuracy * 100.0))
#
# # champions = [translate_champions(["Camille", "Sejuani", "Anivia", "KogMaw", "Karma"],
# #                                  ["Garen", "Viego", "Zed", "Sivir", "Rell"],
# #                                  "riot_id"),
# #              translate_champions(["Camille", "Sejuani", "Qiyana", "KogMaw", "Karma"],
# #                                  ["Garen", "Viego", "Zed", "Sivir", "Rell"],
# #                                  "riot_id")]
#
# champions = [translate_champions(["Camille", "JarvanIV", "Vex", "KogMaw"],
#                                  ["Garen", "Sejuani", "Sylas", "Sivir"],
#                                  "riot_id"), ]
#
# champions = pd.DataFrame(champions)
# y_pred = model.predict_proba(champions)
# print(y_pred)
# y_pred = model.predict(champions)
# print(y_pred)
