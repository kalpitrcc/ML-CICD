import numpy as np
from flask import Flask, request, jsonify
import pickle, boto3, os
app = Flask(__name__)
# Load the model
model = ""


MODELPATH = "s3://mlflow/3/8c3ed6ec528c45caa06d2e6fe06717ec/artifacts/model/model.pkl"

os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://mip-bdcs-vm64.mip.storage.hpecorp.net:10017"
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "admin123"
os.environ["MLFLOW_TRACKING_URI"] = "http://mip-bdcs-vm64.mip.storage.hpecorp.net:10028"
os.environ["MODELPATH"] = MODELPATH


@app.before_first_request
def load_model():
    app.logger.info("Download and loading the Model in Memory.")
    s3 = boto3.client('s3', 
        endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    )

    BUCKET, MODEL = os.environ["MODELPATH"].split("/")[2], "/".join(os.environ["MODELPATH"].split("/")[3:])

    s3.download_file(BUCKET,MODEL, "model.pkl")
    model = pickle.load(open('model.pkl','rb'))

@app.route('/api/prediction', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    # Make prediction using model loaded from disk as per the data.
    prediction = model.predict([[np.array(data['exp'])]])
    # Take the first value of prediction
    output = prediction[0]
    return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
