FROM python:3.8
COPY . /app
WORKDIR /app
ENV PYTHONPATH .
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
COPY *.py /app/
CMD ["python", "./lunchtime/views/main.py"]