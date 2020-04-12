FROM python:3.8.2
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
RUN mkdir /python-etc
COPY ./ /code
WORKDIR /code
RUN pip install --upgrade pip && pip install -r requirements.txt
