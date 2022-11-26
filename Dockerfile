FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt update
RUN apt install -y python3-dev libgmp3-dev libmpfr-dev postgresql \
    postgresql-contrib default-mysql-server libpq-dev default-libmysqlclient-dev libgmp-dev



ENV APP_CONFIG_PATH=/workdir/configs/dep-config.yml
ENV PYCURL_SSL_LIBRARY=openssl


WORKDIR /workdir

COPY . .

EXPOSE 5000
EXPOSE 5500

RUN pip install psycopg2-binary
RUN pip install celery
RUN pip install -r requirements.txt


#CMD ["python", "src/run_web.py"]
