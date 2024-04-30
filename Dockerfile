FROM python:3.11-alpine

WORKDIR /usr/src/app

RUN apk update \ 
  && apk add build-base unzip wget automake autoconf libtool pcre-dev bison

RUN cd /usr/src \
  && wget https://github.com/swig/swig/archive/refs/tags/v3.0.12.zip \
  && unzip v3.0.12.zip \
  && cd swig-3.0.12 \
  && ./autogen.sh \
  && ./configure \
  && make \
  && make install \
  && cd /usr/src/app \
  && rm -rf /usr/src/swig-3.0.12 /usr/src/v3.0.12.zip

RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . .
COPY .env.example .env

ENTRYPOINT ["entrypoint.sh"]