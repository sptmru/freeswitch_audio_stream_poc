#!/bin/bash

sed -i '/<X-PRE-PROCESS cmd="set" data="default_password=[^"]*"\/>/c\<X-PRE-PROCESS cmd="set" data="default_password='"${EXTENSION_PASSWORD:-extensionpassword}"'"\/>' /usr/local/freeswitch/conf/vars.xml

sed '/<!-- <param name="rtp-end-port" value="32768"\/> -->/a \
<param name="rtp-start-port" value="10000"/>\n<param name="rtp-end-port" value="10010"/>' \
-i /usr/local/freeswitch/conf/autoload_configs/switch.conf.xml

NUMBER_TO_DIAL="${NUMBER_TO_DIAL:-99999}"

awk -v numbertodial="$NUMBER_TO_DIAL" '
/<context name="default">/ {
    print
    print ""
    print "<extension name=\"esl_park\">"
    print "  <condition field=\"destination_number\" expression=\"^"numbertodial"$\">"
    print "    <action application=\"park\"\"/>"
    print "  </condition>"
    print "</extension>"
    next
}
{ print }
' /usr/local/freeswitch/conf/dialplan/default.xml > /tmp/default.xml && mv /tmp/default.xml /usr/local/freeswitch/conf/dialplan/default.xml

/usr/local/freeswitch/bin/freeswitch -nonat -nf -nc