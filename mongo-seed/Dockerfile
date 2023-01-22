from mongo

COPY data.json /data.json

CMD mongoimport --host mongodb --db disney --collection Tripadvisor --type json --file /data.json
