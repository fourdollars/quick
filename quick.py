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

import argparse, glob, os, re, shutil, stat, subprocess, sys, urllib, yaml

QUICK = 'https://raw.github.com/fourdollars/quick/master/quick.py'
INDEX = '.index'
REMOTE = 'https://raw.github.com/fourdollars/quick/master/packages/'
REMOTE_INDEX = REMOTE + INDEX
BASE = os.path.join(os.getenv('HOME'), '.local')
PROGRAM = os.path.join(BASE, 'bin', 'quick')
DATA = os.path.join(BASE, 'share', 'quick')
DESKTOP = os.path.join(BASE, 'share', 'applications')
TARGET = os.path.join(BASE, 'lib', 'quick')
PACKAGES = os.path.join(DATA, 'packages')
PAKCAGES_INDEX = os.path.join(PACKAGES, '.index')
INSTALLED = os.path.join(DATA, 'installed')
BINARIES = os.path.join(DATA, 'binaries')

class Quick(object):

    def installable(self, name):
        if not os.path.exists(os.path.join(PACKAGES, name + '.yaml')):
            return False
        if not name in self.packages:
            return True
        from pkg_resources import parse_version
        data = yaml.load(open(os.path.join(PACKAGES, name + '.yaml')).read())
        return parse_version(data['Version']) > parse_version(self.packages[name])

    def showpkg(self, name, version=None):
        if os.path.exists(os.path.join(PACKAGES, name + '.yaml')):
            data = yaml.load(open(os.path.join(PACKAGES, name + '.yaml')).read())
            print('Package: ' + name)
            for field in ['Name', 'Description', 'Version', 'Homepage']:
                if field is 'Version' and version:
                    print(field + ': ' + version)
                else:
                    print(field + ': ' + data[field])
        else:
            print(name + ' is not existed.')

    def searchpkg(self, pattern):
        match = []
        for pkg in open(PAKCAGES_INDEX).read().splitlines():
            found = False
            data = yaml.load(open(os.path.join(PACKAGES, pkg)).read())
            if re.search(pattern, pkg, re.IGNORECASE):
                found = True
            else:
                for field in ['Name', 'Description']:
                    if re.search(pattern, data[field], re.IGNORECASE):
                        found = True
                        break
            if found:
                if not pkg.split('.')[0] in match:
                    match.append(pkg.split('.')[0])
        return match

    def installpkg(self, name, quiet=False, verbose=False):
        data = yaml.load(open(os.path.join(PACKAGES, name + '.yaml')).read())
        folder = ''
        if 'Folder' in data:
            folder = data['Folder']
        target = os.path.join(TARGET, name)
        command_succeed = False
        for item in data['Download']:
            url = None
            arch = None
            sha1 = None
            try:
                # TODO: check sha1sum
                url, arch, sha1 = item.split(' ')
            except:
                url, arch = item.split(' ')
            if arch == 'all' or arch == os.uname()[4]:
                folder = ''
                if 'Folder' in data:
                    folder = data['Folder']
                filename = os.path.basename(url)
                # Don't download binary package again.
                if not os.path.exists(os.path.join(BINARIES, filename)):
                    if verbose:
                        print('Downloading ' + url + ' to ' + os.path.join(BINARIES, filename))
                    elif not quiet:
                        print('Downloading ' + url)
                    urllib.urlretrieve(url, os.path.join(BINARIES, filename))
                if verbose:
                    print('Uncompressing ' + filename + ' to ' + target)
                if not os.path.exists(target):
                    os.makedirs(target)
                command = None
                if filename.endswith('.zip'):
                    if verbose:
                        command = ['unzip', '-o', os.path.join(BINARIES, filename), '-d', target]
                    else:
                        command = ['unzip', '-qo', os.path.join(BINARIES, filename), '-d', target]
                else:
                    if verbose:
                        command = ['tar', 'xvf', os.path.join(BINARIES, filename), '-C', target]
                    else:
                        command = ['tar', 'xf', os.path.join(BINARIES, filename), '-C', target]
                if subprocess.call(command) == 0:
                    command_succeed = True
        if command_succeed:
            self.packages[name] = data['Version']
            # Create symbolic links
            if 'Symlink' in data:
                for symlink in data['Symlink']:
                    source = os.path.join(target, folder, symlink)
                    link = os.path.join(BASE, 'bin', symlink)
                    if verbose:
                        print('Creating a symbolic link ' + link + ' -> ' + source)
                    if os.path.exists(link):
                        os.remove(link)
                    os.symlink(source, link)
            # Create desktop files
            if 'DesktopFile' in data and 'Exec' in data['DesktopFile']:
                if verbose:
                    print('Creating a desktop file ' + os.path.join(DESKTOP, name + '.desktop'))
                desktop = data['DesktopFile']
                with open(os.path.join(DESKTOP, name + '.desktop'), "w") as desktopfile:
                    desktopfile.write("[Desktop Entry]\n")
                    desktopfile.write("Type=Application\n")
                    desktopfile.write("Name=" + data['Name'] + "\n")
                    if 'Comment' in desktop:
                        desktopfile.write("Comment=" + desktop['Comment'] + "\n")
                    if 'Categories' in desktop:
                        desktopfile.write("Categories=" + desktop['Categories'] + "\n")
                    desktopfile.write("Exec=\"" + os.path.join(target, folder, desktop['Exec']) + "\"\n")
                    if 'Icon' in desktop:
                        desktopfile.write("Icon=" + os.path.join(target, folder, desktop['Icon']) + "\n")
                    desktopfile.write("Terminal=false\n")
                    desktopfile.write("StartupNotify=true\n")
            shutil.copy(os.path.join(PACKAGES, name + '.yaml'), os.path.join(INSTALLED, name + '.yaml'))
            if not quiet:
                print(name + " installation complete.")

    def removepkg(self, name):
        pkg = os.path.join(INSTALLED, name + '.yaml')
        data = yaml.load(open(pkg).read())
        if 'Symlink' in data:
            for symlink in data['Symlink']:
                path = os.path.join(BASE, 'bin', symlink)
                if os.path.exists(path):
                    os.remove(path)
        if 'DesktopFile' in data:
            path = os.path.join(DESKTOP, name + '.desktop')
            if os.path.exists(path):
                os.remove(path)
        path = os.path.join(TARGET, name)
        if os.path.exists(path):
            shutil.rmtree(path)
        del self.packages[name]
        if os.path.exists(pkg):
            os.remove(pkg)

    def update(self, args):
        if args.verbose:
            print('[INDEX] Fetching ' + REMOTE_INDEX + ' and saving to ' + PAKCAGES_INDEX)
        elif not args.quiet:
            print('[INDEX] Fetching ' + REMOTE_INDEX)
        urllib.urlretrieve(REMOTE_INDEX, PAKCAGES_INDEX)
        lines = open(PAKCAGES_INDEX).read().splitlines()
        for i, line in enumerate(lines):
            if args.verbose:
                print('[' + str(i + 1) + '/' + str(len(lines)) + '] ' + 'Fetching ' + REMOTE + line + ' and saving to ' + os.path.join(PACKAGES, line))
            elif not args.quiet:
                print('[' + str(i + 1) + '/' + str(len(lines)) + '] ' + 'Fetching ' + REMOTE + line)
            urllib.urlretrieve(REMOTE + line, os.path.join(PACKAGES, line))

    def list(self, args):
        for pkg in open(PAKCAGES_INDEX).read().splitlines():
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
                print('')

    def install(self, args):
        for pkg in args.packages:
            for name in open(PAKCAGES_INDEX).read().splitlines():
                name = name.split('.')[0]
                if name == pkg:
                    if args.force:
                        self.installpkg(pkg, args.quiet, args.verbose)
                    else:
                        for pkg in self.packages.keys():
                            if pkg == name and not self.installable(name):
                                print(name + " is the latest version.")
                                break
                        else:
                            self.installpkg(pkg, args.quiet, args.verbose)
    def installed(self, args):
        for name, version in self.packages.iteritems():
            if args.verbose:
                self.showpkg(name, version)
                print('')
            else:
                print(name + " " + version)

    def remove(self, args):
        for name in args.packages:
            if name in self.packages:
                print("Removing " + name)
                self.removepkg(name)
                print(name + " is removed.")
            else:
                print("There is no such package named as " + name + ".")

    def upgrade(self, args):
        # TODO
        print("Upgrade all packages.")

    def self_upgrade(self, args):
        print('Fetching ' + QUICK + ' and saving to ' + PROGRAM)
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

    def sanity_check(self):
        if not os.path.exists(PACKAGES):
            os.makedirs(PACKAGES)
        if not os.path.exists(BINARIES):
            os.makedirs(BINARIES)
        if not os.path.exists(DESKTOP):
            os.makedirs(DESKTOP)
        if not os.path.exists(INSTALLED):
            os.makedirs(INSTALLED)

    def __init__(self):
        self.packages = {}

        self.sanity_check()

        for pkg in glob.glob(INSTALLED + "/*.yaml"):
            data = yaml.load(open(pkg).read())
            name = os.path.basename(pkg).split('.')[0]
            version = data['Version']
            self.packages[name] = version

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
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.installed, parser=parser)

        command = subparsers.add_parser('remove', help='remove is identical to install except that packages are removed instead of installed.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.add_argument('packages', nargs='*')
        command.set_defaults(func=self.remove, parser=parser)

        command = subparsers.add_parser('upgrade', help='upgrade is used to install the newest versions of all packages currently installed.')
        command.add_argument("-q", "--quiet", help="Quiet; produces output suitable for logging, omitting progress indicators.", action="store_true")
        command.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
        command.set_defaults(func=self.upgrade, parser=parser)

        command = subparsers.add_parser('self-upgrade', help='self-upgrade is used to upgrade this program itself.')
        command.set_defaults(func=self.self_upgrade, parser=parser)

        command = subparsers.add_parser('clean', help='clean clears out the local repository of retrieved package files.')
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
