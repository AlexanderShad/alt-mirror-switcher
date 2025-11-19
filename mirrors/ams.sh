#!/usr/bin/env bash
# #
# Description: installing or removing additional mirrors
# Autor: Aleksandr Shamaraev <shad@altlinux.org>
# License: GPLv2+
# URL: https://altlinux.space/aleksandershad
#

if [[ -n "$1" ]]; then
	case "$1" in
		-i)
			if [ $(rpm --eval %_priority_distbranch) = "sisyphus" ]
				then
					cp -a *sisyphus.list /etc/apt/sources.list.d/
                else
                    cp -a *branch.list /etc/apt/sources.list.d/
			fi
		;;
		-r)
			rm /etc/apt/sources.list.d/ams_*.list
		;;
	esac
fi
