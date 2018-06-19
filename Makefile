all: build-ui
	./setup.py build

install: install-ui
	mkdir -p $(DESTDIR)/var/www/contractor/api
	mkdir -p $(DESTDIR)/etc/apache2/sites-available
	mkdir -p $(DESTDIR)/etc/contractor
	mkdir -p $(DESTDIR)/usr/lib/contractor/cron
	mkdir -p $(DESTDIR)/usr/lib/contractor/util
	mkdir -p $(DESTDIR)/var/lib/contractor/

	install -m 644 api/contractor.wsgi $(DESTDIR)/var/www/contractor/api
	install -m 644 apache.conf $(DESTDIR)/etc/apache2/sites-available/contractor.conf
	install -m 644 master.conf.sample $(DESTDIR)/etc/contractor
	install -m 755 lib/cron/* $(DESTDIR)/usr/lib/contractor/cron
	install -m 755 lib/util/* $(DESTDIR)/usr/lib/contractor/util

	./setup.py install --root $(DESTDIR) --install-purelib=/usr/lib/python3/dist-packages/ --prefix=/usr --no-compile -O0

test-requires:
	python3-pytest python3-pytest-cov python3-pytest-django python3-pytest-mock

test:
	py.test-3 -x --cov=contractor --cov-report html --cov-report term --ds=contractor.settings -vv contractor

build-ui:
	# cd ui ; npm install
	cd ui ; npm run build

install-ui:
	mkdir -p $(DESTDIR)/var/www/contractor/ui/
	install -m 644 ui/build/* $(DESTDIR)/var/www/contractor/ui/
	install -m 644 ui/src/www/* $(DESTDIR)/var/www/contractor/ui/
	echo "window.API_BASE_URI = 'http://' + window.location.hostname;" > $(DESTDIR)/var/www/contractor/ui/env.js

clean-ui:
	$(RM) -fr ui/build

clean: clean-ui
	./setup.py clean
	$(RM) -fr build
	$(RM) -f dpkg

.PHONY:: test build-ui install-ui clean-ui

respkg-distros:
	echo xenial

respkg-requires:
	echo respkg

respkg:
	cd resources && respkg -b ../contractor-os-base_0.0.respkg -n contractor-os-base -e 0.0 -c "Contractor - OS Base" -t load_os_base.sh -d os_base
	touch respkg

respkg-file:
	echo $(shell ls *.respkg)

.PHONY:: respkg-distros respkg-requires respkg respkg-file

dpkg-distros:
	echo xenial

dpkg-requires:
	echo dpkg-dev debhelper cdbs python3-dev python3-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	echo $(shell ls ../contractor_*.deb):xenial

.PHONY:: dpkg-distros dpkg-requires dpkg dpkg-file
