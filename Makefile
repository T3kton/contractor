all: build-ui

install: install-ui

test-requires:
	python3-pytest python3-pytest-cov python3-pytest-django python3-pytest-mock

test:
	py.test-3 -x --cov=contractor --cov-report html --cov-report term --ds=contractor.settings -vv contractor

build-ui:
	cd ui ; npm run build

install-ui:
	mkdir -p $(DESTDIR)/var/www/contractor/ui/
	cp ui/build/* $(DESTDIR)/var/www/contractor/ui/
	cp ui/src/www/* $(DESTDIR)/var/www/contractor/ui/

clean-ui:
	rm -fr ui/build

clean: clean-ui

dpkg-distros:
	echo xenial

dpkg-requires:
	echo dpkg-dev debhelper cdbs python3-dev python3-setuptools

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

.PHONY: test build-ui install-ui clean-ui dpkg-distros dpkg-requires dpkg
