#!/bin/sh

echo "Got base path at '$1'"
echo "Got curent version of '$2'"
echo "Got previsous version of '$3'"

/usr/local/contractor/util/blueprintLoader ${1}usr/local/contractor/resources/base_os.toml
