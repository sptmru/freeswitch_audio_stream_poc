FROM debian:bookworm

RUN apt-get update \
  && apt-get install -y gnupg2 wget lsb-release git cmake

# Download the GPG key for the repository
RUN wget --http-user=signalwire --http-password=pat_EoSrCyJGQgW89pasdEeggfCw \
  -O /usr/share/keyrings/signalwire-freeswitch-repo.gpg \
  https://freeswitch.signalwire.com/repo/deb/debian-release/signalwire-freeswitch-repo.gpg

# Create apt auth.conf with credentials
RUN echo "machine freeswitch.signalwire.com login signalwire password pat_EoSrCyJGQgW89pasdEeggfCw" > /etc/apt/auth.conf

# Add the SignalWire repository to sources list
RUN echo "deb [signed-by=/usr/share/keyrings/signalwire-freeswitch-repo.gpg] https://freeswitch.signalwire.com/repo/deb/debian-release/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/freeswitch.list \
  && echo "deb-src [signed-by=/usr/share/keyrings/signalwire-freeswitch-repo.gpg] https://freeswitch.signalwire.com/repo/deb/debian-release/ $(lsb_release -sc) main" >> /etc/apt/sources.list.d/freeswitch.list

RUN apt-get update \
  && apt-get build-dep -y freeswitch \
  && apt-get install -y libjsoncpp-dev \
  && apt-get clean 

RUN cd /usr/local/src \
  && git clone https://github.com/signalwire/freeswitch.git -bv1.10 freeswitch \
  && cd freeswitch \
  && git config pull.rebase true

COPY ./modules.conf /usr/local/src/freeswitch/modules.conf

RUN cd /usr/local/src/freeswitch \
  && ./bootstrap.sh -j \
  && ./configure \
  && make && make install && make cd-sounds-install cd-moh-install

RUN cd /usr/local/src \
  && git clone https://github.com/sptmru/freeswitch_mod_audio_stream \
  && cd freeswitch_mod_audio_stream \
  && git checkout openai-new \
  && git submodule update --init --recursive \
  && mkdir build && cd build \
  && export PKG_CONFIG_PATH=/usr/local/freeswitch/lib/pkgconfig \
  && cmake -DCMAKE_BUILD_TYPE=Release .. \
  && make && make install

RUN sed -i '/<load module="mod_logfile"\/>/a \    <load module="mod_audio_stream"/>' /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml
RUN sed -i '/<load module="mod_signalwire"\/>/a \    <load module="mod_avmd"/>' /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml
RUN sed -i 's|<param name="listen-ip" value="::"/>|<param name="listen-ip" value="0.0.0.0"/>|g' /usr/local/freeswitch/conf/autoload_configs/event_socket.conf.xml
RUN sed -i 's|<!--<param name="apply-inbound-acl" value="loopback.auto"/>-->|<param name="apply-inbound-acl" value="lan"/>|' /usr/local/freeswitch/conf/autoload_configs/event_socket.conf.xml
RUN sed -i '/<list name="lan" default="allow">/,/<\/list>/c\<list name="lan" default="allow">\n      <node type="allow" cidr="0.0.0.0/0"/>\n<\/list>' /usr/local/freeswitch/conf/autoload_configs/acl.conf.xml

EXPOSE 5060 5060/udp 8021
RUN ln -s /usr/local/freeswitch/bin/fs_cli /usr/local/bin/fs_cli

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]
