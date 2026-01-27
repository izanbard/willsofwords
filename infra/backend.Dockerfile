FROM python:latest
WORKDIR /app
RUN pip install --root-user-action ignore -U pip setuptools wheel
COPY requirements.txt requirements.txt
RUN pip install --root-user-action ignore -U -r requirements.txt
COPY . .
EXPOSE 5000
CMD [ "python", "-u", "-m", "backend"]