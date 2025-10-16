# storage/Python
FROM python:3.12.12-trixie
WORKDIR /usr/src/app

# dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8100
CMD [ "python", "./app.py" ]
