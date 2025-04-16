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
                ("education", OneHotEncoder(), ["Education_Level"]),
                ("experience", "passthrough", ["Years_of_Experience"])
            ]
        )

    def train(self):
        # Load the dataset
        df = pd.read_csv("career_path_dataset.csv")
        

        # Define features and target
        X = df[["Skills", "Years_of_Experience", "Education_Level"]]
        y = df["Job_ID"]

        # Create the pipeline
        self.clf = make_pipeline(self.preprocessor, self.alg)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

        # Train the model
        self.clf.fit(X, y)

        # Predict
        y_pred = self.clf.predict(X_test)

        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        fscore = f1_score(y_test, y_pred, average='weighted')

        values = (accuracy, precision, recall, fscore)
        print("Model Evaluation:", values)
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
