#!/usr/bin/env bash

CURRENT_RUBY=`ruby -v`

if [[ -r $HOME/edx_all/edx-platform/.ruby-version ]]; then
  RUBY_VER=`cat $HOME/edx_all/edx-platform/.ruby-version`
fi

CLEAN_RUBY_VER=`echo $RUBY_VER | tr -d '-'`

if [[ "${CURRENT_RUBY#*$CLEAN_RUBY_VER}" != "$CURRENT_RUBY" ]]; then
	echo "SUCCESS!"
else
	echo "FAILURE!"
fi