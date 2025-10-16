# storage/Python
FROM python:3.12.12-trixie
WORKDIR /usr/src/app

# dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8090
CMD [ "python", "./app.py" ]
