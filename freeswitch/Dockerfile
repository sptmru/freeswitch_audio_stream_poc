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
  && git clone https://github.com/amigniter/mod_audio_stream \
  && cd mod_audio_stream \
  && git submodule update --init --recursive \
  && mkdir build && cd build \
  && cmake -DCMAKE_BUILD_TYPE=Release .. \
  && make && make install

RUN sed -i '/<load module="mod_logfile"\/>/a \    <load module="mod_audio_stream"/>' /usr/local/freeswitch/conf/autoload_configs/modules.conf.xml

CMD ["/usr/local/freeswitch/bin/freeswitch"]
