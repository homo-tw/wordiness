FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04

# 基本工具
RUN apt-get update && apt-get install -y \
    python3-pip ffmpeg git && \
    ln -s /usr/bin/python3 /usr/bin/python

# Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製程式
COPY . /app
WORKDIR /app

# 啟動
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]