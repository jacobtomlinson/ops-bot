FROM python:3.7-alpine
LABEL maintainer="Jacob Tomlinson <jacob@tom.linson.uk>"

RUN apk update && apk add --no-cache gcc musl-dev git openssh-client

WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir --no-use-pep517 .

# Copy source
COPY opsdroid opsdroid
COPY setup.py setup.py
COPY versioneer.py versioneer.py
COPY setup.cfg setup.cfg
COPY README.md README.md
COPY MANIFEST.in MANIFEST.in
 
RUN apk del gcc musl-dev

EXPOSE 8080

CMD ["opsdroid", "start"]
