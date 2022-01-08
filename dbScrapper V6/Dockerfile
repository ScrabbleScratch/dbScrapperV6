FROM python:3
WORKDIR /scrapper
ADD . .
ENV URL=""
ENV HOST=""
ENV DATABASE=""
ENV COLLECTION=""
ENV START=0
ENV FINISH=0
ENV DELAY=2.5
ENV RETRY=3
ENV STATUS="config/status.json"
RUN pip install -r requirements.txt
VOLUME /scrapper
CMD python dbScrapperV6.py $URL $HOST $DATABASE $COLLECTION --start $START --finish $FINISH --delay $DELAY --retry $RETRY --status $STATUS
