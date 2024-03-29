FROM python:3.8.0-slim

# Copy local code to the container image
COPY src /src/
COPY requirements.txt /src/requirements.txt
COPY healthstaffconnect-e913cb44aef7.json /src/healthstaffconnect-e913cb44aef7.json
# COPY src/config/.env 
# COPY healthstaffconnect-e913cb44aef7.json /src/healthstaffconnect-e913cb44aef7.json
# Sets the working directory
WORKDIR /src

# Upgrade PIP
RUN pip install --upgrade pip
# RUN pip3 install --user -U nltk
# RUN python -m nltk.downloader all-corpora
#Install python libraries from requirements.txt
RUN pip3 install -r requirements.txt
ENV GOOGLE_APPLICATION_CREDENTIALS=healthstaffconnect-e913cb44aef7.json
# Set $PORT environment variable
ENV PORT 8080
EXPOSE 8080
# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 600 main:app