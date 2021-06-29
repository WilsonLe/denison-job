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
	xvfb \
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

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

RUN apt-get update && apt-get install -y \
	google-chrome-stable

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION 92.0.4515.43
ENV CHROMEDRIVER_DIR /chromedriver

RUN mkdir $CHROMEDRIVER_DIR
# Download and install Chromedriver
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

EXPOSE 7345

CMD ["venv/bin/python", "main.py"]