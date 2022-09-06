FROM python:3.9

COPY requirements.txt requirements.txt

RUN pip3 install -r  \
    requirements.txt \
    --no-cache-dir \
    --ignore-installed

COPY . /workdir
WORKDIR /workdir

RUN chmod -R 777 tree_tagger_lib

CMD ["gunicorn", "app:server"]
