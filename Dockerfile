FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /ingestevents
WORKDIR /ingestevents

ADD requirements.txt /ingestevents/
RUN pip install -r requirements.txt

ADD entrypoint.sh /ingestevents/
RUN chmod +x entrypoint.sh

ADD test.sh /ingestevents/
RUN chmod +x test.sh

ADD ingestevents/. /ingestevents/

EXPOSE 80

ENTRYPOINT ["/ingestevents/entrypoint.sh"]