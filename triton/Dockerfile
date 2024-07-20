FROM nvcr.io/nvidia/tritonserver:22.05-py3

ENV TZ Asia/Seoul
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive


RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

ENTRYPOINT ["tritonserver"]
CMD ["--model-repository=/models"]
