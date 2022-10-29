FROM python:3.10-bullseye as builder
RUN pip install -U pip
WORKDIR /work
COPY . /work
RUN pip install .[prod]

FROM python:3.10-slim-bullseye as runner
LABEL org.opencontainers.image.title="Gcrostore"
LABEL org.opencontainers.image.description="A web application of Crostore with Gmail and Google Sheets integrated"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Shuhei Nitta(@huisint)"
RUN useradd crostore
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 80
CMD ["uvicorn", "gcrostore:app", "--host", "0.0.0.0", "--port", "80"]
