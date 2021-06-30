FROM ubuntu
USER root
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /app

COPY requirements.txt ./
COPY . .

# INSTALL SYSTEM DEPENDENCIES
RUN apt-get update && apt-get install -y \
	sudo \
	wget \
	unzip \
	xvfb \
	libxi6 \
	libgconf-2-4 \
	build-essential \
	ibglib2.0-dev \
	libcap2-bin \
	python3.9 \
	python3-venv \
	python3-dotenv \
	python3-flask \
	&& rm -rf /var/lib/apt/lists/*

# INSTALL SERVER DEPENDENCIES
RUN python3 -m venv venv \
	&& venv/bin/pip install -r requirements.txt 

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub \
    | apt-key add

RUN sudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

RUN apt-get -y update \
    && apt-get -y install google-chrome-stable

RUN wget https://chromedriver.storage.googleapis.com/92.0.4515.43/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
	&& sudo mv chromedriver /usr/bin/chromedriver \
	&& sudo chown root:root /usr/bin/chromedriver \
	&& sudo chmod +x /usr/bin/chromedriver

ENV PYTHON_ENV production
EXPOSE 7345

CMD ["venv/bin/python", "main.py"]