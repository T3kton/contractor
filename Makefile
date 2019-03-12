VERSION := $(shell head -n 1 debian/changelog | awk '{match( $$0, /\(.+?\)/); print substr( $$0, RSTART+1, RLENGTH-2 ) }' | cut -d- -f1 )

all: build-ui
	./setup.py build

install: install-ui
	mkdir -p $(DESTDIR)/var/www/contractor/api
	mkdir -p $(DESTDIR)/etc/apache2/sites-available
	mkdir -p $(DESTDIR)/etc/contractor
	mkdir -p $(DESTDIR)/usr/lib/contractor/cron
	mkdir -p $(DESTDIR)/usr/lib/contractor/util
	mkdir -p $(DESTDIR)/usr/lib/contractor/setup

	install -m 644 api/contractor.wsgi $(DESTDIR)/var/www/contractor/api
	install -m 644 apache.conf $(DESTDIR)/etc/apache2/sites-available/contractor.conf
	install -m 644 master.conf.sample $(DESTDIR)/etc/contractor
	install -m 755 lib/cron/* $(DESTDIR)/usr/lib/contractor/cron
	install -m 755 lib/util/* $(DESTDIR)/usr/lib/contractor/util
	install -m 755 lib/setup/* $(DESTDIR)/usr/lib/contractor/setup

	./setup.py install --root $(DESTDIR) --install-purelib=/usr/lib/python3/dist-packages/ --prefix=/usr --no-compile -O0

version:
	echo $(VERSION)

clean: clean-ui
	./setup.py clean
	$(RM) -fr build
	$(RM) -f dpkg
	$(RM) -fr htmlcov
	dh_clean || true

dist-clean: clean

.PHONY:: all install version clean dist-clean

ui_files := $(foreach file,$(wildcard ui/src/www/*),ui/build/$(notdir $(file)))

build-ui: ui/build/bundle.js $(ui_files)

ui/build/bundle.js: $(wildcard ui/src/frontend/component/*) ui/src/frontend/index.js
	cd ui && npm run build

ui/build/%:
	cp ui/src/www/$(notdir $@) $@

install-ui: build-ui
	mkdir -p $(DESTDIR)/var/www/contractor/ui/
	install -m 644 ui/build/* $(DESTDIR)/var/www/contractor/ui/
	echo "window.API_BASE_URI = 'http://' + window.location.hostname;" > $(DESTDIR)/var/www/contractor/ui/env.js

clean-ui:
	$(RM) -fr ui/build

.PHONY:: build-ui install-ui clean-ui

test-distros:
	echo ubuntu-xenial

test-requires:
	python3-pytest python3-pytest-cov python3-pytest-django python3-pytest-mock python3-pytest-timeout

test:
	py.test-3 -x --cov=contractor --cov-report html --cov-report term --ds=contractor.settings -vv contractor

.PHONY:: test-distros test-requires test

dpkg-distros:
	echo ubuntu-xenial

dpkg-requires:
	echo dpkg-dev debhelper python3-dev python3-setuptools nodejs npm nodejs-legacy

dpkg-setup:
	cd ui && npm install

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	echo $(shell ls ../contractor_*.deb):xenial

.PHONY:: dpkg-distros dpkg-requires dpkg dpkg-file
