import numpy as np
from flask import Flask, request, jsonify
import pickle, boto3, os
app = Flask(__name__)
# Load the model
model = ""

@app.before_first_request
def load_model():
    global model
    app.logger.info("Download and loading the Model in Memory.")
    s3 = boto3.client('s3', 
        endpoint_url=os.environ["S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        aws_session_token=None,
        config=boto3.session.Config(signature_version='s3v4'),
        verify=False
    )

    BUCKET, MODEL = os.environ["MODELPATH"].split("/")[2], "/".join(os.environ["MODELPATH"].split("/")[3:])

    s3.download_file(BUCKET.strip(),MODEL.strip(), "model.pkl")
    model = pickle.load(open('model.pkl','rb'))

@app.route('/api/prediction', methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    app.logger.info(data)
    # Make prediction using model loaded from disk as per the data.
    prediction = model.predict(data["data"]).tolist()
    # Take the first value of prediction
    app.logger.info(prediction)
    return jsonify({"prediction": prediction})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
