FROM python:latest
LABEL MAINTAINER="Hamidreza Azarbad | hamidreza.azarbad77@gmail.com"

ENV PYTHONUNBUFFERED 1

RUN mkdir /similarity_race_bot
WORKDIR /similarity_race_bot
COPY . /similarity_race_bot
RUN mkdir backup
RUN mkdir backup/leader_boards
RUN mkdir backup/potential_boards
RUN mkdir user_images
RUN mkdir config
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "race_bot.py"]