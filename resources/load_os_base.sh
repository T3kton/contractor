#!/bin/sh

echo "Got base path at '$1'"
echo "Got curent version of '$2'"
echo "Got previsous version of '$3'"

/usr/lib/contractor/util/blueprintLoader ${1}usr/lib/contractor/resources/base_os.toml
