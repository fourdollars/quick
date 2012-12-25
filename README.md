# Quick installation helper for GNU/Linux

## Intrdoduction

Quick is an installation helper to download and install binary packages from Internet to ~/.local

## Prerequisite

* bash
* python (2.7.x)
* python-yaml
* python-pkg-resources
* tar
* unzip
* wget

## Installation

    $ wget http://bit.ly/quick-installer -O - | bash -

And then logout the system and login the system again.

## Usage

Update packages list.

    $ quick update

List available packages.

    $ quick list

Search for packages.

    $ quick search text

Install packages.

    $ quick install sublime-text

Remove packages.

    $ quick remove sublime-text

More usage

    $ quick

## Package

You are welcome to provide more packages to Quick.

Please refer to the files of https://github.com/fourdollars/quick/tree/master/packages

The file name of yaml should meet this regex pattern "^[a-z][-a-z0-9]&#42;&#92;.yaml&#36;".

[Mandatory]

* Name
* Description
* Version
* Download

[Optional]

* Folder
* Symlink
* DesktopFile

## Uninstallation

    $ quick self-upgrade
    $ quick remove -a
    $ rm -fr ~/.local/bin/quick ~/.local/lib/quick ~/.local/share/quick
