# syntax=docker/dockerfile:1

FROM ubuntu
FROM python:3.8 

# set working directory
WORKDIR //c/Users/Craig/Projects/TradingBot/alpaca_bot/

# add files to look at
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

COPY . . 
CMD ["python","./main.py"]
# CMD ["python","main.py"]




