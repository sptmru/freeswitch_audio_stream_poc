FROM debian:bookworm

ARG BUILD_CPUS=1

RUN apt-get update \
  && apt-get install -y --quiet --no-install-recommends \
    gnupg2 wget lsb-release git cmake \
    python-is-python3 lsof gcc g++ make build-essential git autoconf automake default-mysql-client redis-tools \
    curl telnet libtool libtool-bin libssl-dev libcurl4-openssl-dev libz-dev liblz4-tool \
    libxtables-dev libip6tc-dev libip4tc-dev  libiptc-dev libavformat-dev liblua5.1-0-dev libavfilter-dev libavcodec-dev libswresample-dev \
    libevent-dev libpcap-dev libxmlrpc-core-c3-dev markdown libjson-glib-dev lsb-release libpq-dev php-dev \
    libhiredis-dev gperf libspandsp-dev default-libmysqlclient-dev htop dnsutils gdb libtcmalloc-minimal4 \
    gnupg2 wget pkg-config ca-certificates libjpeg-dev libsqlite3-dev libpcre3-dev libldns-dev libboost-all-dev \
    libspeex-dev libspeexdsp-dev libedit-dev libtiff-dev yasm libswscale-dev haveged libre2-dev \
    libopus-dev libsndfile-dev libshout3-dev libmpg123-dev libmp3lame-dev libopusfile-dev libgoogle-perftools-dev \
  # && apt-get build-dep -y freeswitch \
  && apt-get clean 

RUN cd /usr/local/src \
  && git clone https://github.com/freeswitch/spandsp.git && cd spandsp && git checkout 0d2e6ac \
  && ./bootstrap.sh && ./configure && make -j ${BUILD_CPUS} && make install

RUN cd /usr/local/src \
  && git clone --depth 1 -b v1.13.17 https://github.com/freeswitch/sofia-sip.git \
  && cd sofia-sip \
  && ./bootstrap.sh && ./configure && make -j ${BUILD_CPUS} && make install

RUN cd /usr/local/src \
  && git clone https://github.com/signalwire/freeswitch.git -bv1.10 freeswitch \
  && cd freeswitch \
  && git config pull.rebase true

COPY ./modules.conf /usr/local/src/freeswitch/modules.conf

RUN ldconfig

RUN cd /usr/local/src/freeswitch \
  && ./bootstrap.sh -j \
  && ./configure \
  && make && make install && make cd-sounds-install cd-moh-install

RUN cd /usr/local/src \
  && git clone https://github.com/sptmru/freeswitch_mod_audio_stream \
  && cd freeswitch_mod_audio_stream \
  && git submodule update --init --recursive \
  && mkdir build && cd build \
  && export PKG_CONFIG_PATH=/usr/local/freeswitch/lib/pkgconfig \
  && cmake -DCMAKE_BUILD_TYPE=Release .. \
  && make && make install

RUN sed -i 's|<load module="mod_verto"/>|<load module="mod_audio_stream"/>|' /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml
RUN sed -i 's|<load module="mod_signalwire"/>|<load module="mod_avmd"/>|' /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml
RUN sed -i 's|<param name="listen-ip" value="::"/>|<param name="listen-ip" value="0.0.0.0"/>|g' /usr/local/freeswitch/conf/autoload_configs/event_socket.conf.xml
RUN sed -i 's|<!--<param name="apply-inbound-acl" value="loopback.auto"/>-->|<param name="apply-inbound-acl" value="lan"/>|' /usr/local/freeswitch/conf/autoload_configs/event_socket.conf.xml
RUN sed -i '/<list name="lan" default="allow">/,/<\/list>/c\<list name="lan" default="allow">\n      <node type="allow" cidr="0.0.0.0/0"/>\n<\/list>' /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml

EXPOSE 5060 5060/udp 8021
RUN ln -s /usr/local/freeswitch/bin/fs_cli /usr/local/bin/fs_cli

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
