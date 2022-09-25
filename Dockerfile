FROM python:3.10-bullseye as builder
RUN pip install -U pip
WORKDIR /work
COPY . /work
RUN pip install .[pro]

FROM python:3.10-slim-bullseye as runner
RUN useradd crostore
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
EXPOSE 8080
CMD [ "gunicorn", "gcrostore:app", "-b", "0.0.0.0:8080", "--worker-class", "uvicorn.workers.UvicornWorker"]
