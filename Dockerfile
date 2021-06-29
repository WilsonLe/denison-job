FROM ubuntu
USER root
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /app

COPY requirements.txt ./
COPY . .

# INSTALL SYSTEM DEPENDENCIES
RUN apt-get update && apt-get install -y \
	sudo \
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

EXPOSE 7345

CMD ["venv/bin/python", "main.py"]