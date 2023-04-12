FROM python:3.7
RUN apt-get install --fix-missing \
&& apt-get update \
&& apt-get install -y python3-pip python3-dev libpq-dev default-libmysqlclient-dev \
&& apt-get install -y vim
WORKDIR /src/backend
COPY requirements.txt /src/backend
RUN ls
RUN pip3 install -r requirements.txt
COPY . /src/backend
EXPOSE 8000
ENTRYPOINT ["sh", "entrypoint.sh"]
