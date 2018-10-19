# -*- coding: utf-8 -*-
#
# Copyright © 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate translation-finder
# <https://github.com/WeblateOrg/translation-finder>
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
#
"""Filesystem finder for translations."""
from __future__ import unicode_literals, absolute_import

from fnmatch import fnmatch

try:
    from pathlib import Path, PurePath
except ImportError:
    from pathlib2 import Path, PurePath

EXCLUDES = frozenset((".git", ".hg", ".eggs", "*.swp", "__pycache__"))


class Finder(object):
    """Finder for files which might be considered translations."""

    def __init__(self, root, files=None):
        if not isinstance(root, PurePath):
            root = Path(root)
        self.root = root
        if files is None:
            files = self.list_files(root)
        relatives = (path.relative_to(root) for path in files)
        self.files = {path.as_posix(): path for path in relatives}
        self.lc_files = {path.lower(): obj for path, obj in self.files.items()}

    def list_files(self, root):
        """Recursively list files in a path.

        It skips excluded files."""
        for path in root.iterdir():
            if any((path.match(exclude) for exclude in EXCLUDES)):
                continue
            if path.is_dir():
                for ret in self.list_files(path):
                    yield ret
            else:
                yield path

    def has_file(self, name):
        """Check whether file exists."""
        return name in self.files

    def filter_files(self, glob, dirglob=None):
        """Filter lowercase file names against glob."""
        for name, path in self.lc_files.items():
            try:
                directory, filename = name.rsplit("/", 1)
            except ValueError:
                filename = name
                directory = None

            if dirglob and (directory is None or not fnmatch(directory, dirglob)):
                continue

            if fnmatch(filename, glob):
                yield path
