FROM python:3
ENV PYTHONUNBUFFERED=1
ENV PATH $PATH:./
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
