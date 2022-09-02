FROM arm64v8/postgres
USER root
RUN apt update && apt install -y postgresql-14-postgis-3

# libsodium
RUN apt-get update && apt-get install -y make git postgresql-server-dev-14 curl build-essential libreadline-dev zile
RUN curl -s -L https://github.com/theory/pgtap/archive/v1.1.0.tar.gz | tar zxvf - && cd pgtap-1.1.0 && make && make install
RUN curl -s -L https://download.libsodium.org/libsodium/releases/libsodium-1.0.18.tar.gz | tar zxvf - && cd libsodium-1.0.18 && ./configure && make check && make install

# pgxn client
RUN apt-get update \
    && apt-get install -y postgresql-plperl-9.5 build-essential postgresql-server-dev-9.5 curl git-core python3-pip cpanminus \
    && rm -rf /var/lib/apt/lists/*
RUN curl -LO https://raw.githubusercontent.com/miyagawa/cpanminus/master/cpanm \
    && chmod +x cpanm \
    && ./cpanm -n Digest::HMAC_SHA1 \
    && rm -fr ./cpanm /root/.cpanm
RUN pip install pgxnclient

# pgsodium extension
RUN pgxn install pgsodium

# update postgres config
RUN echo "shared_preload_libraries = 'pgsodium'" >> /var/lib/postgresql/data/postgresql.conf

# add postgres init script(s)
COPY ./init.sh docker-entrypoint-initdb.d/init.sh
COPY ./pgsodium_getkey /usr/share/postgresql/14/extension/pgsodium_getkey