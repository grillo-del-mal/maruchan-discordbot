FROM fedora:23

RUN dnf install -y --nogpgcheck gcc redhat-rpm-config python3 python3-pip \
    python3-devel libsodium-devel python3-ipython git libffi-devel

RUN pip3 install git+https://github.com/Rapptz/discord.py@async

ADD maruchan /src
ADD config.json /src/config.json

WORKDIR /src

CMD python3 maruchan.py
