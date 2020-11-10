FROM python:3.8
RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential tesseract-ocr libtesseract-dev libgl1-mesa-glx
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt
COPY . /app
CMD python3 app.py 0.0.0.0:5000