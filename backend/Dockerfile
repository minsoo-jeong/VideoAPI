FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel

ENV TZ Asia/Seoul
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive


RUN apt update && \
    apt install -y vim tzdata openssh-server git wget net-tools libgl1-mesa-glx software-properties-common

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN echo 'root:root' |chpasswd


WORKDIR /workspace
ADD . .

RUN pip install -r requirements.txt
