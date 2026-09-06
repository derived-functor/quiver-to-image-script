FROM texlive/texlive:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        pdf2svg \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /data
