FROM python:3.8

ADD maruchan/requirements.txt /src/requirements.txt

RUN pip3 install -r /src/requirements.txt

ADD maruchan /src

WORKDIR /src

CMD python3 maruchan.py
