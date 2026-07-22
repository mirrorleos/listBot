FROM python:3.9.16-slim-buster

# Installa watchdog per l’autoreload
RUN pip install watchdog

# Directory dove monterai il volume
WORKDIR /bot

# Installa sempre i requirements dal volume
# e avvia script.py con autoreload
CMD sh -c "\
    pip install -r requirements.txt && \
    watchmedo auto-restart --patterns='*.py' --recursive -- python script.py \
"