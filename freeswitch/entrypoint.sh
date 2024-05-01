#!/bin/bash

sed -i '/<X-PRE-PROCESS cmd="set" data="default_password=[^"]*"\/>/c\<X-PRE-PROCESS cmd="set" data="default_password='"${EXTENSION_PASSWORD:-extensionpassword}"'"\/>' /usr/local/freeswitch/conf/vars.xml

ESL_APP_HOST="${ESL_APP_HOST:-esl-app}"
ESL_APP_PORT="${ESL_APP_PORT:-8022}"
NUMBER_TO_DIAL="${NUMBER_TO_DIAL:-99999}"

awk -v host="$ESL_APP_HOST" -v port="$ESL_APP_PORT" -v numbertodial="$NUMBER_TO_DIAL" '
/<context name="default">/ {
    print
    print ""
    print "<extension name=\"esl_inbound\">"
    print "  <condition field=\"destination_number\" expression=\"^"numbertodial"$\">"
    print "    <action application=\"socket\" data=\"" host ":" port " async full\"/>"
    print "  </condition>"
    print "</extension>"
    next
}
{ print }
' /usr/local/freeswitch/conf/dialplan/default.xml > /tmp/default.xml && mv /tmp/default.xml /usr/local/freeswitch/conf/dialplan/default.xml

/usr/local/freeswitch/bin/freeswitch -nonat -nf -nc