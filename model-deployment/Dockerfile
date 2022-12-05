FROM python:3.9
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libgl1 -y
RUN mkdir -p /data/image
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
CMD ["/usr/local/bin/gunicorn", "main:app", "-w", "5", "--threads", "3", "-b", "0.0.0.0:8000"]