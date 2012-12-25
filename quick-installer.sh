#!/bin/bash
# -*- coding: utf-8; indent-tabs-mode: nil; tab-width: 4; c-basic-offset: 4; -*-
#
# Copyright (C) 2012 Shih-Yuan Lee (FourDollars) <fourdollars@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

if ! grep "\$HOME/.local/bin" $HOME/.profile > /dev/null 2>&1; then
    cat >> $HOME/.profile <<ENDLINE

if [ -d "\$HOME/.local/bin" ] ; then
    PATH="\$PATH:\$HOME/.local/bin"
fi
ENDLINE
fi

[ ! -d "$HOME/.local/bin" ] && mkdir -p "$HOME/.local/bin"

wget https://raw.github.com/fourdollars/quick/master/quick.py -O $HOME/.local/bin/quick && chmod +x $HOME/.local/bin/quick

# vim:fileencodings=utf-8:expandtab:tabstop=4:shiftwidth=4:softtabstop=4
