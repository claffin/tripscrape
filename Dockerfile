FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y libgconf-2-4 libnss3 libxss1 apt-utils
RUN apt-get install -y fonts-liberation libappindicator3-1 xdg-utils libasound2 libatk-bridge2.0-0 libatspi2.0-0 libgbm1 libgtk-3-0
RUN apt-get install -y software-properties-common
RUN apt-get install -y curl wget unzip
RUN apt-get install -y xvfb

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome*.deb
RUN apt-get install -y -f

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python","./main.py"]