# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

EXPOSE 8501

WORKDIR /Streamlit
RUN apt-get update && \
    apt-get install -y build-essential \
    software-properties-common \
    git \
    default-libmysqlclient-dev \
    locales locales-all && \
    rm -rf /var/lib/apt/lists/* 

ENV LC_ALL fr_FR_UTF-8
ENV LANG fr_FR_UTF-8
ENV LANGUAGE fr_FR_UTF-8
COPY . .

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader wordnet
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader punkt
ENV PYTHONPATH "{PYTHONPATH}:/."

CMD [ "streamlit", "run", "1_🎉_Home.py", "--server.port=8501","--server.address=0.0.0.0"]