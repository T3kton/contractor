*/15 * * * * root [ -x /usr/lib/contractor/cron/genDNS ] && /usr/lib/contractor/cron/genDNS
*/5 * * * * root [ -x /usr/lib/contractor/cron/postMaster ] && /usr/lib/contractor/cron/postMaster
10 1 1 * 0 root [ -x /usr/lib/contractor/util/manage.py ] && /usr/lib/contractor/util/manage.py clearsessions
