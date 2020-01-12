FROM python:3-slim
ADD . /app
WORKDIR /app

RUN pip install --target=/app/build /app/.

ENV PYTHONPATH /app/build
ENV PATH="/app/build/bin:${PATH}"

ENTRYPOINT ["repo-admin"]
