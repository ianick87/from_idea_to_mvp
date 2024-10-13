import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
import joblib
from django.conf import settings
from django.db import connection
import os
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


class AiService:
    def __init__(self):
        self.model_path = os.path.join(
            settings.BASE_DIR, "autoDiagnosis", "services", "model.pkl"
        )
        self.model = None

    def data_pipeline(self):
        from autoDiagnosis.models import Data

        data = Data.objects.all().values()
        df = pd.DataFrame(data)
        if df.empty:
            raise ValueError("No data available for training.")

        # Drop unnecessary columns
        df = df.drop(columns=["id", "name"])

        # Convert categorical variables
        df["gender"] = df["gender"].map({"M": 0, "F": 1})
        df["headache"] = df["headache"].astype(int)
        df["stomach_pain"] = df["stomach_pain"].astype(int)
        df["throat_pain"] = df["throat_pain"].astype(int)
        df["has_disease"] = df["has_disease"].astype(int)

        # Handle blood_pressure (Assuming format '120/80')
        bp_split = df["blood_pressure"].str.split("/", expand=True)
        df["systolic_bp"] = bp_split[0].astype(float)
        df["diastolic_bp"] = bp_split[1].astype(float)
        df = df.drop("blood_pressure", axis=1)

        # Reorder columns
        columns = [col for col in df.columns if col != "has_disease"] + ["has_disease"]
        df = df[columns]

        return df

    def train_model(self):
        # Prepare the data
        df = self.data_pipeline()
        X = df.iloc[:, :-1]  # Features
        y = df.iloc[:, -1]  # Target

        # Initialize and train the model
        self.model = LGBMClassifier()
        self.model.fit(X, y)

        # Make predictions
        y_pred = self.model.predict(X)

        # Calculate performance metrics
        accuracy = accuracy_score(y, y_pred)
        precision = precision_score(y, y_pred, zero_division=1)
        recall = recall_score(y, y_pred)
        f1 = f1_score(y, y_pred)
        conf_matrix = confusion_matrix(y, y_pred)

        # Save the trained model to a file
        joblib.dump(self.model, self.model_path)

        # Return the model and the performance metrics as a dictionary
        return {
            "model": self.model,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": conf_matrix,
        }

    def get_prediction(self, input_data):
        if not self.model:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                raise FileNotFoundError(
                    "Model not found. Please train the model first."
                )
        prediction = self.model.predict([input_data])
        confidence = self.model.predict_proba([input_data])
        return prediction[0], confidence.max()
