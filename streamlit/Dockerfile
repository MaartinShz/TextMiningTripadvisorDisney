FROM python:3.9-slim-buster

EXPOSE 8501

WORKDIR /streamlit
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
ENV PYTHONPATH "{PYTHONPATH}:/."

CMD [ "streamlit", "run", "1_🎉_Home.py", "--server.port=8501","--server.address=0.0.0.0"]
