FROM python:3.8.11
ENV HOME /root
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
WORKDIR /root
COPY . .
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait
EXPOSE 5000
CMD ["flask", "run"]