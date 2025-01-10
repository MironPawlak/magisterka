# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# django.setup()
import numpy as np
import pandas as pd
import pickle
from django.core.management import BaseCommand
from sklearn.metrics import brier_score_loss, accuracy_score

from xgboost import XGBClassifier

from apps.matches.management.commands.create_csv import translate_champions


"""
Czas gry
różnica w Gold earned
różnica w Experience
różnica w Strukturze
różnica w killach
"""


class Command(BaseCommand):

    def handle(self, *args, **options):
        def brier(preds, dtrain):
            labels = dtrain.get_label()
            preds = 1 / (1 + np.exp(-preds))
            grad = preds - labels
            hess = preds * (1 - preds)
            return grad, hess

        # file = "matches_class.csv"
        file = "data/matches.csv"
        # FEATURES = 70
        FEATURES = 169
        dataframe = pd.read_csv(file, header=None)

        X_test = dataframe.sample(frac=0.1)
        X_train = dataframe.drop(X_test.index)

        Y_test = X_test.pop(FEATURES)
        Y_train = X_train.pop(FEATURES)

        model = XGBClassifier()
        model.fit(X_train, Y_train)

        preds = model.predict(X_test)
        brier_score = brier_score_loss(Y_test, preds)
        print(f"Brier Score: {brier_score:.4f}")

        predictions = [round(value) for value in preds]
        accuracy = accuracy_score(Y_test, predictions)
        print("Accuracy: %.2f%%" % (accuracy * 100.0))

        # with open('data/model.pkl', 'wb') as f:
        #     pickle.dump(model, f)

        # print("Accuracy: %.2f%%" % (accuracy * 100.0))

        # champions = [translate_champions(["Camille", "Sejuani", "Anivia", "KogMaw", "Karma"],
        #                                  ["Garen", "Viego", "Zed", "Sivir", "Rell"],
        #                                  "riot_id"),
        #              translate_champions(["Camille", "Sejuani", "Qiyana", "KogMaw", "Karma"],
        #                                  ["Garen", "Viego", "Zed", "Sivir", "Rell"],
        #                                  "riot_id")]

        # dtrain = xgb.DMatrix(X_train, label=Y_train)
        # dtest = xgb.DMatrix(X_test, label=Y_test)
        #
        # def brier(preds, dtrain):
        #     labels = dtrain.get_label()
        #     preds = 1 / (1 + np.exp(-preds))
        #     grad = preds - labels
        #     hess = preds * (1 - preds)
        #     return grad, hess
        #
        # params = {
        #     "objective": "binary:logistic",  # Base logistic regression
        #     # "eval_metric": "accuracy",  # Logloss for monitoring
        #     "max_depth": 6,
        #     "eta": 0.1,
        # }
        #
        # model = xgb.train(
        #     params,
        #     dtrain,
        #     early_stopping_rounds=50,
        #     num_boost_round=1000,
        #     obj=brier,
        #     evals=[(dtest, "test")],
        #     verbose_eval=True
        # )

        # champions = [translate_champions(["Camille", "JarvanIV", "Sylas", "Sivir"],
        #                                  ["Garen", "Sejuani", "Vex", "KogMaw"],
        #                                  "riot_id"), ]
        #
        #
        # champions = pd.DataFrame(champions)
        # y_pred = model.predict_proba(champions)
        # print(y_pred)
        # y_pred = model.predict(champions)
        # print(y_pred)
