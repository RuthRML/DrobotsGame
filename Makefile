#!/usr/bin/make -f
# -*- mode:makefile -*-

start-grid: /tmp/db/registry /tmp/db/nodouno /tmp/db/nododos /tmp/db/nodotres
	icegridnode	--Ice.Config=nodouno.config &
	while ! netstat -lptn 2> /dev/null | grep ":4061"; do sleep 1; done
	icegridnode	--Ice.Config=nododos.config &
	icegridnode	--Ice.Config=nodotres.config &
	cp -r /home/ruth/Escritorio/EntregableFinal /tmp/Distribuidos/ &
	chmod u+x /tmp/Distribuidos/* &
	icegridadmin --Ice.Config=locator.config -uuser -ppass -e "application add 'application.xml'" &
	icegridadmin --Ice.Config=locator.config -uuser -ppass -e "application update 'application.xml'"

stop-grid:
	for node in nododos nodouno nodotres; do \
	    icegridadmin --Ice.Config=locator.config -uuser -ppass -e "node shutdown $$node"; \
	done
	killall icegridnode

/tmp/db/%:
	mkdir -p $@

clean: stop-grid
	rm *~
	rm -r /tmp/db
