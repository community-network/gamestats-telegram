FROM python:3

WORKDIR /usr/src/app

ENV token ''
ENV redishost redis-availability.1e8uve.ng.0001.euc1.cache.amazonaws.com
ENV redisport 6379
ENV redispass ''

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# https://github.com/goverfl0w/discord-interactions/
COPY . .

CMD python ./app.py
