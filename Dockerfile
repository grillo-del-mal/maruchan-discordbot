FROM python:3.6.1

ADD maruchan/requirements.txt /src/requirements.txt

RUN pip3 install -r /src/requirements.txt

ADD maruchan /src

WORKDIR /src

CMD python3 maruchan.py
