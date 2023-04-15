FROM python:3.10-bullseye as builder
WORKDIR /work
COPY . /work
RUN pip install --no-cache-dir . uvicorn==0.21.1

FROM python:3.10-slim-bullseye as runner
LABEL org.opencontainers.image.title="Gcrostore"
LABEL org.opencontainers.image.description="A web application of Crostore with Gmail and Google Sheets integrated"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Shuhei Nitta(@huisint)"
RUN useradd crostore
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 80
ENTRYPOINT [ "uvicorn", "gcrostore:app", "--host", "0.0.0.0" ]
CMD [ "--port", "80"]
