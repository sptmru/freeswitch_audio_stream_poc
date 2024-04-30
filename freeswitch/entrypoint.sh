#!/bin/bash

sed -i '/<X-PRE-PROCESS cmd="set" data="default_password=[^"]*"\/>/c\<X-PRE-PROCESS cmd="set" data="default_password='"${EXTENSION_PASSWORD:-extensionpassword}"'"\/>' /usr/local/freeswitch/conf/vars.xml

/usr/local/freeswitch/bin/freeswitch -nonat -nf -nc