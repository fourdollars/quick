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

import argparse, os, re, shutil, stat, sys, urllib, yaml

QUICK = 'https://raw.github.com/fourdollars/quick/master/quick.py'
PROGRAM = os.path.join(os.getenv('HOME'), '.local', 'bin', 'quick')
REMOTE = 'https://raw.github.com/fourdollars/quick/master/packages/'
DATA = os.path.join(os.getenv('HOME'), '.local', 'share', 'quick')
PACKAGES = os.path.join(DATA, 'packages')
INDEX = os.path.join(PACKAGES, 'index')
INSTALLED = os.path.join(DATA, 'installed')

class Quick(object):

    def showpkg(self, name):
        if os.path.exists(os.path.join(PACKAGES, name + '.yaml')):
            data = yaml.load(open(os.path.join(PACKAGES, name + '.yaml')).read())
            print('Package: ' + name)
            for field in ['Name', 'Description', 'Version', 'Homepage']:
                print(field + ': ' + data[field])
        else:
            print(name + ' is not existed.')

    def searchpkg(self, pattern):
        found = False
        match = []
        for pkg in open(INDEX).read().splitlines():
            data = yaml.load(open(os.path.join(PACKAGES, pkg)).read())
            if re.search(pattern, pkg):
                found = True
            else:
                for field in ['Name', 'Description']:
                    if re.search(pattern, data[field]):
                        found = True
                        break
            if found:
                for name in match:
                    if name == pkg.split('.')[0]:
                        break
                else:
                    match.append(pkg.split('.')[0])

        return match

    def update(self, args):
        if not os.path.exists(PACKAGES):
            os.makedirs(PACKAGES)
        if args.verbose:
            print('[INDEX] Fetching ' + REMOTE + 'index' + ' and saving to ' + INDEX)
        elif not args.quiet:
            print('[INDEX] Fetching ' + REMOTE + 'index')
        urllib.urlretrieve(REMOTE + 'index', INDEX)
        lines = open(INDEX).read().splitlines()
        for i, line in enumerate(lines):
            if args.verbose:
                print('[' + str(i + 1) + '/' + str(len(lines)) + '] ' + 'Fetching ' + REMOTE + line + ' and saving to ' + os.path.join(PACKAGES, line))
            elif not args.quiet:
                print('[' + str(i + 1) + '/' + str(len(lines)) + '] ' + 'Fetching ' + REMOTE + line)
            urllib.urlretrieve(REMOTE + line, os.path.join(PACKAGES, line))

    def list(self, args):
        for pkg in open(INDEX).read().splitlines():
            data = yaml.load(open(os.path.join(PACKAGES, pkg)).read())
            print(pkg.split('.')[0] + " - " + data['Description'])

    def search(self, args):
        if args.pattern:
            names = self.searchpkg(args.pattern)
            for name in names:
                self.showpkg(name)
                print('')

    def info(self, args):
        if args.packages:
            for pkg in args.packages:
                self.showpkg(pkg)

    def install(self, args):
        # TODO
        for pkg in args.packages:
            print("Install " + pkg)

    def remove(self, args):
        # TODO
        for pkg in args.packages:
            print("Remove " + pkg)

    def upgrade(self, args):
        # TODO
        print("Upgrade all packages.")

    def self_upgrade(self, args):
        if args.verbose:
            print('Fetching ' + QUICK + ' and saving to ' + PROGRAM)
        elif not args.quiet:
            print('Fetching ' + QUICK)
        urllib.urlretrieve(QUICK, PROGRAM)
        st = os.stat(PROGRAM)
        os.chmod(PROGRAM, st.st_mode | stat.S_IEXEC)

    def clean(self, args):
        if os.path.exists(PACKAGES):
            shutil.rmtree(PACKAGES)
            os.makedirs(PACKAGES)

    def __init__(self):
        parser = argparse.ArgumentParser(prog='quick', description='Quick is an installation helper to download and install binary packages from Internet to ~/.local')
        parser.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        parser.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        subparsers = parser.add_subparsers()

        command = subparsers.add_parser('update', help='update is used to resynchronize the package index files from their sources.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.update, parser=parser)

        command = subparsers.add_parser('list', help='list prints out an available packages list to stdout.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.list, parser=parser)

        command = subparsers.add_parser('search', help='search performs a full text search on all available package lists.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument('pattern')
        command.set_defaults(func=self.search, parser=parser)

        command = subparsers.add_parser('info', help='info is used to display information about the packages listed on the command line.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument('packages', nargs='+')
        command.set_defaults(func=self.info, parser=parser)

        command = subparsers.add_parser('install', help='install is followed by one or more packages desired for installation or upgrading.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument('packages', nargs='+')
        command.set_defaults(func=self.install, parser=parser)

        command = subparsers.add_parser('remove', help='remove is identical to install except that packages are removed instead of installed.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument('packages', nargs='+')
        command.set_defaults(func=self.remove, parser=parser)

        command = subparsers.add_parser('upgrade', help='upgrade is used to install the newest versions of all packages currently installed.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.upgrade, parser=parser)

        command = subparsers.add_parser('self-upgrade', help='self-upgrade is used to upgrade this program itself.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.self_upgrade, parser=parser)

        command = subparsers.add_parser('clean', help='clean clears out the local repository of retrieved package files.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.clean, parser=parser)

        if len(sys.argv) == 1:
            parser.print_help()
        else:
            args = parser.parse_args()
            if args:
                args.func(args)

if __name__ == '__main__':
    Quick()

# vim:fileencodings=utf-8:expandtab:tabstop=4:shiftwidth=4:softtabstop=4
