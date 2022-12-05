FROM python:3.9
RUN apt-get update
RUN mkdir -p /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt
COPY preprocessing.py /app/preprocessing.py
COPY training.py /app/training.py
WORKDIR /app
CMD ["/bin/bash"]