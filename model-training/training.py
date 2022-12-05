import pandas as pd
import mlflow
import json
import os
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LogisticRegression


# Set path to inputs
PROCESSED_DATA_DIR = os.environ["PROCESSED_DATA_DIR"]
train_data_file = 'train.csv'
train_data_path = os.path.join(PROCESSED_DATA_DIR, train_data_file)

test_data_file = 'test.csv'
test_data_path = os.path.join(PROCESSED_DATA_DIR, test_data_file)

#EXPERIMENT_NAME = os.environ["EXPERIMENT_NAME"]
EXPERIMENT_NAME = "cicd"
mlflow.set_experiment(EXPERIMENT_NAME)
EXPERIMENT_ID = mlflow.get_experiment_by_name(EXPERIMENT_NAME).experiment_id

# Read train data
df = pd.read_csv(train_data_path, sep=",")

# Split data into dependent and independent variables
X_train = df.drop('income', axis=1)
y_train = df['income']


# Read test data
df = pd.read_csv(test_data_path, sep=",")

# Split data into dependent and independent variables
X_test = df.drop('income', axis=1)
y_test = df['income']

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


with mlflow.start_run(run_name='Logistic Regression', experiment_id=EXPERIMENT_ID) as run:
    logreg = LogisticRegression(solver='lbfgs', max_iter=110)
    logreg.fit(X_train, y_train)

    predicted_qualities = logreg.predict(X_test)

    (rmse, mae, r2) = eval_metrics(y_test, predicted_qualities)
    accuracy = round(logreg.score(X_test, y_test) * 100, 2)
    print("  RMSE: %s" % rmse)
    print("  MAE: %s" % mae)
    print("  R2: %s" % r2)
    print("  Accuracy: %s" % accuracy)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2", r2)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("accuracy", accuracy)
    
    mlflow.sklearn.log_model(logreg, "model")
    print("Model: {}/model".format(run.info.artifact_uri))
