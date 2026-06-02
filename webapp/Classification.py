import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, accuracy_score, recall_score, confusion_matrix


class Classification:
    def __init__(self, alg):
        self.alg = alg
        self.clf = None
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("skills", CountVectorizer(tokenizer=lambda x: x.split(", "), token_pattern=None), "Skills"),
                # handle_unknown='ignore' so education levels not seen during
                # training (or arbitrary user input at predict time) don't crash.
                ("education", OneHotEncoder(handle_unknown='ignore'), ["Education_Level"]),
                ("experience", "passthrough", ["Years_of_Experience"])
            ]
        )

    def train(self):
        # Load the dataset using a path relative to the project root so it
        # works regardless of the current working directory (e.g. gunicorn).
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dataset_path = os.path.join(base_dir, "career_path_dataset.csv")
        df = pd.read_csv(dataset_path)

        # Define features and target. Job_ID is unique per row (an identifier,
        # not a class), so we predict the job *title*, which has real classes.
        X = df[["Skills", "Years_of_Experience", "Education_Level"]]
        y = df["Predicted_Job_Title"]

        # Create the pipeline
        self.clf = make_pipeline(self.preprocessor, self.alg)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        # Train the model on the training split only (avoid data leakage so the
        # reported metrics reflect performance on unseen data).
        self.clf.fit(X_train, y_train)

        # Predict on the held-out test set
        y_pred = self.clf.predict(X_test)

        # Evaluate (zero_division=0 avoids warnings/NaNs for unseen classes)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        fscore = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        values = (accuracy, precision, recall, fscore)
        return values


        

    def predict(self, skills, years_of_experience, education_level):
        if self.clf is None:
            raise Exception("Model not trained yet. Call the train() method first.")

        # Create a DataFrame for prediction
        data = pd.DataFrame([{
            "Skills": skills,
            "Years_of_Experience": years_of_experience,
            "Education_Level": education_level
        }])

        # Predict using the trained pipeline
        prediction = self.clf.predict(data)
        return prediction[0]
