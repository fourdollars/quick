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

import argparse, os, re, shutil, stat, subprocess, sys, urllib, yaml

QUICK = 'https://raw.github.com/fourdollars/quick/master/quick.py'
REMOTE = 'https://raw.github.com/fourdollars/quick/master/packages/'
BASE = os.path.join(os.getenv('HOME'), '.local')
PROGRAM = os.path.join(BASE, 'bin', 'quick')
DATA = os.path.join(BASE, 'share', 'quick')
DESKTOP = os.path.join(BASE, 'share', 'applications')
TARGET = os.path.join(BASE, 'lib')
PACKAGES = os.path.join(DATA, 'packages')
BINARIES = os.path.join(DATA, 'binaries')
INDEX = os.path.join(PACKAGES, 'index')
INSTALLED = os.path.join(DATA, 'installed')


class Quick(object):

    def installable(self, name):
        if not os.path.exists(os.path.join(PACKAGES, name + '.yaml')):
            return False
        if not name in self.packages:
            return True
        from pkg_resources import parse_version
        data = yaml.load(open(os.path.join(PACKAGES, name + '.yaml')).read())
        return parse_version(data['Version']) > parse_version(self.packages[name])

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

    def installpkg(self, pkg, quiet=False, verbose=False):
        data = yaml.load(open(os.path.join(PACKAGES, pkg + '.yaml')).read())
        for item in data['Downloads']:
            url = None
            arch = None
            sha1 = None
            try:
                # TODO: check sha1sum
                url, arch, sha1 = item.split(' ')
            except:
                url, arch = item.split(' ')
            if arch == 'all' or arch == os.uname()[4]:
                filename = os.path.basename(url)
                # Don't download binary package again.
                if not os.path.exists(os.path.join(BINARIES, filename)):
                    if verbose:
                        print('Downloading ' + url + ' to ' + os.path.join(BINARIES, filename))
                    elif not quiet:
                        print('Downloading ' + url)
                    urllib.urlretrieve(url, os.path.join(BINARIES, filename))
                if verbose:
                    print('Uncompressing ' + filename)
                command = None
                if filename.endswith('.zip'):
                    if verbose:
                        command = ['unzip', '-o', os.path.join(BINARIES, filename), '-d', TARGET]
                    else:
                        command = ['unzip', '-qo', os.path.join(BINARIES, filename), '-d', TARGET]
                else:
                    if verbose:
                        command = ['tar', 'xvf', os.path.join(BINARIES, filename), '-C', TARGET]
                    else:
                        command = ['tar', 'xf', os.path.join(BINARIES, filename), '-C', TARGET]
                if subprocess.call(command) == 0:
                    self.packages[pkg] = data['Version']
                    # Create symbolic links
                    if 'Links' in data:
                        for k, v in data['Links'].iteritems():
                            source = os.path.join(BASE, v)
                            target = os.path.join(BASE, k)
                            if verbose:
                                print('Creating a symbolic link ' + target + ' -> ' + source)
                            if os.path.exists(target):
                                os.remove(target)
                            os.symlink(source, target)
                    # Create desktop files
                    if 'DesktopFile' in data and 'Exec' in data['DesktopFile']:
                        if verbose:
                            print('Creating a desktop file ' + os.path.join(DESKTOP, pkg + '.desktop'))
                        desktop = data['DesktopFile']
                        if not os.path.exists(DESKTOP):
                            os.makedirs(DESKTOP)
                        with open(os.path.join(DESKTOP, pkg + '.desktop'), "w") as desktopfile:
                            desktopfile.write("[Desktop Entry]\n")
                            desktopfile.write("Type=Application\n")
                            desktopfile.write("Name=" + data['Name'] + "\n")
                            if 'Comment' in desktop:
                                desktopfile.write("Comment=" + desktop['Comment'] + "\n")
                            if 'Categories' in desktop:
                                desktopfile.write("Categories=" + desktop['Categories'] + "\n")
                            desktopfile.write("Exec=" + os.path.join(BASE, desktop['Exec']) + "\n")
                            if 'Icon' in desktop:
                                desktopfile.write("Icon=" + os.path.join(BASE, desktop['Icon']) + "\n")
                            desktopfile.write("Terminal=false\n")
                            desktopfile.write("StartupNotify=true\n")
                    with open(INSTALLED, "w") as installed:
                        for k, v in self.packages.iteritems():
                            installed.write(k + " " + v + "\n")
                    if not quiet:
                        print(pkg + " installation complete.")

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
        if not os.path.exists(BINARIES):
            os.makedirs(BINARIES)
        if not os.path.exists(INSTALLED):
            open(INSTALLED, 'w').close()
        for pkg in args.packages:
            for name in open(INDEX).read().splitlines():
                name = name.split('.')[0]
                if name == pkg:
                    if args.force:
                        self.installpkg(pkg, args.quiet, args.verbose)
                    else:
                        for installed in open(INSTALLED).read().splitlines():
                            if installed.split(' ')[0] == name and not self.installable(name):
                                print(name + " is the latest version.")
                                break
                        else:
                            self.installpkg(pkg, args.quiet, args.verbose)
    def installed(self, args):
        if not os.path.exists(INSTALLED):
            open(INSTALLED, 'w').close()
        for installed in open(INSTALLED).read().splitlines():
            field = installed.split(' ')
            name, version = field[0:2]
            print(name + " " + version)

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
        if os.path.exists(BINARIES):
            shutil.rmtree(BINARIES)
            os.makedirs(BINARIES)

    def __init__(self):
        self.packages = {}
        self.folders = {}
        if not os.path.exists(INSTALLED):
            open(INSTALLED, 'w').close()
        for installed in open(INSTALLED).read().splitlines():
            field = installed.split(' ')
            name, version = field[0:2]
            folder = ' '.join(field[2:])
            self.packages[name] = version
            self.packages[name] = folder

        parser = argparse.ArgumentParser(prog='quick', description='Quick is an installation helper to download and install binary packages from Internet to ~/.local')
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
        command.add_argument("-f", "--force", help="force install.", action="store_true")
        command.add_argument('packages', nargs='+')
        command.set_defaults(func=self.install, parser=parser)

        command = subparsers.add_parser('installed', help='list installed packages.')
        command.set_defaults(func=self.installed, parser=parser)

        command = subparsers.add_parser('remove', help='remove is identical to install except that packages are removed instead of installed.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument("-a", "--all", help="remove all packages.", action="store_true")
        command.add_argument('packages', nargs='*')
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
