#! /usr/bin/env python
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

import argparse, os, sys, urllib

DATA = os.path.join(os.getenv('HOME'), '.local', 'share', 'quick')
INDEX = os.path.join(DATA, 'index')

def list(args):
    print("List *")

def search(args):
    if args.packages:
        for pkg in args.packages:
            print("Search " + pkg)

def info(args):
    if args.packages:
        for pkg in args.packages:
            print("Info " + pkg)

def install(args):
    for pkg in args.packages:
        print("Install " + pkg)

def remove(args):
    for pkg in args.packages:
        print("Remove " + pkg)

def update(args):
    if not os.path.exists(DATA):
        os.makedirs(DATA)
    urllib.urlretrieve('https://raw.github.com/fourdollars/quick/master/packages/index', INDEX)

def upgrade(args):
    print("Upgrade all packages.")

def self_upgrade(args):
    print("Self Upgrade")

def main():
    parser = argparse.ArgumentParser(prog='quick', description='quick is an installation helper to download and install binary packages from Internet to ~/.local')
    parser.add_argument("--verbose", help="increase output verbosity.", action="store_true")
    subparsers = parser.add_subparsers()

    command = subparsers.add_parser('list', help='list prints out an available packages list to stdout.')
    command.set_defaults(func=list, parser=parser)

    command = subparsers.add_parser('search', help='search performs a full text search on all available package lists.')
    command.add_argument('packages', nargs='+')
    command.set_defaults(func=search, parser=parser)

    command = subparsers.add_parser('info', help='info is used to display information about the packages listed on the command line.')
    command.add_argument('packages', nargs='+')
    command.set_defaults(func=info, parser=parser)

    command = subparsers.add_parser('install', help='install is followed by one or more packages desired for installation or upgrading.')
    command.add_argument('packages', nargs='+')
    command.set_defaults(func=install, parser=parser)

    command = subparsers.add_parser('remove', help='remove is identical to install except that packages are removed instead of installed.')
    command.add_argument('packages', nargs='+')
    command.set_defaults(func=remove, parser=parser)

    command = subparsers.add_parser('update', help='update is used to resynchronize the package index files from their sources.')
    command.set_defaults(func=update, parser=parser)

    command = subparsers.add_parser('upgrade', help='upgrade is used to install the newest versions of all packages currently installed.')
    command.set_defaults(func=upgrade, parser=parser)

    command = subparsers.add_parser('self-upgrade', help='self-upgrade is used to upgrade this program itself.')
    command.set_defaults(func=self_upgrade, parser=parser)

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args:
            args.func(args)

if __name__ == '__main__':
    main()

# vim:fileencodings=utf-8:expandtab:tabstop=4:shiftwidth=4:softtabstop=4
