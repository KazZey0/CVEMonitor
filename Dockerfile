FROM python:alpine
WORKDIR /monitor
COPY ./teleMonitor.py /monitor/teleMonitor.py
COPY ./init-db.sql /monitor/init-db.sql
RUN apk add sqlite sqlite-dev gcc musl-dev 
RUN pip install requests pysqlite3 pyTelegramBotAPI
RUN echo "sqlite3 monitor.db -init init-db.sql" | sh
