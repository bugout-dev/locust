FROM python:3.8.6-slim-buster

RUN mkdir /locust

COPY . /locust

RUN cd /locust && python /locust/setup.py install

ENTRYPOINT [ "locust" ]
CMD [ "-h" ]
