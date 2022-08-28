FROM python:3.9

COPY requirements.txt requirements.txt

RUN pip3 install -r  \
    requirements.txt \
    --no-cache-dir \
    --ignore-installed

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:80", "app:server"]
