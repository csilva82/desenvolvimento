FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh \
    | BINDIR=/usr/local/bin sh
ARG WITH_ESP32=1
RUN arduino-cli core update-index && arduino-cli core install arduino:avr \
 && if [ "$WITH_ESP32" = "1" ]; then \
      arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json \
      && arduino-cli core update-index && arduino-cli core install esp32:esp32; \
    fi
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV HOST=0.0.0.0
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-5000} --timeout 600 --workers 1 --threads 4 server:app"]
