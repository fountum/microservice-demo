# storage/Python
FROM python:3.13-alpine
WORKDIR /usr/src/app

# dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8100
CMD [ "python", "./app.py" ]
