#!/bin/bash

sed -i '/<X-PRE-PROCESS cmd="set" data="default_password=[^"]*"\/>/c\<X-PRE-PROCESS cmd="set" data="default_password='"${EXTENSION_PASSWORD:-extensionpassword}"'"\/>' /usr/local/freeswitch/conf/vars.xml

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

echo "127.0.0.1 vosk-server" | tee -a /etc/hosts > /dev/null

/usr/local/freeswitch/bin/freeswitch -nonat -nf -nc