FROM python:3.12-slim
WORKDIR /app
COPY src /app/src
COPY dashboard /app/dashboard
COPY data/raw /app/data/raw
COPY config /app/config
COPY run.py /app/run.py
RUN groupadd --gid 10001 pmo && useradd --uid 10001 --gid 10001 --no-create-home pmo && mkdir /app/state /app/output && chown pmo:pmo /app/state /app/output
USER 10001:10001
EXPOSE 8765
CMD ["python", "run.py", "--bind", "0.0.0.0"]
