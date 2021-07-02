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

RUN wget --no-check-certificate -qO - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - \
    && sudo echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -qqy \
    && apt-get -qqy install google-chrome-stable \
    && rm /etc/apt/sources.list.d/google-chrome.list \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN wget https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
	&& mv /app/chromedriver /usr/bin

ENV PYTHON_ENV production

EXPOSE 7345

CMD ["venv/bin/python", "main.py"]  