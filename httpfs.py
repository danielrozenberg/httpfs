#!/usr/bin/env python

from errno import EIO, ENOENT
import logging
from stat import S_IFDIR, S_IFREG
from sys import argv, exit
from threading import Timer
from time import time

import requests
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

CLEANUP_INTERVAL = 60
CLEANUP_EXPIRED = 60


class HttpFs(LoggingMixIn, Operations):
    """A read only http/https/ftp filesystem."""

    def __init__(self, _schema):
        self.schema = _schema

        self.files = dict()
        self.cleanup_thread = self._generate_cleanup_thread(start=False)

    def init(self, path):
        self.cleanup_thread.start()

    def getattr(self, path, fh=None):
        if path.endswith('..'):
            url = '%s:/%s' % (self.schema, path[:-2])
            r = requests.get(url)
            if r.status_code == 200:
                content = r.content
                attr = dict(st_mode=(S_IFREG | 0o644), st_nlink=1,
                            st_size=len(content), st_ctime=time(), st_mtime=time(),
                            st_atime=time())
                self.files[path] = dict(time=time(), attr=attr, content=content)
                return attr
            else:
                raise FuseOSError(ENOENT)
        else:
            return dict(st_mode=(S_IFDIR | 0o555), st_nlink=2)

    def read(self, path, size, offset, fh):
        if self.files[path]:
            return self.files[path]['content'][offset:offset + size]
        raise FuseOSError(EIO)

    def destroy(self, path):
        self.cleanup_thread.cancel()

    def cleanup(self):
        now = time()
        num_files_before = len(self.files)
        self.files = {k: v for k, v in self.files.items() if now - v['time'] < CLEANUP_EXPIRED}
        num_files_after = len(self.files)
        if num_files_before != num_files_after:
            logging.debug('Truncated cache from %d to %d files' % (num_files_before, num_files_after))
        self.cleanup_thread = self._generate_cleanup_thread()

    def _generate_cleanup_thread(self, start=True):
        cleanup_thread = Timer(CLEANUP_INTERVAL, self.cleanup)
        cleanup_thread.daemon = True

        if start:
            cleanup_thread.start()

        return cleanup_thread

if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <mountpoint> <http|https|ftp>' % argv[0])
        exit(1)

    mountpoint = argv[1]
    schema = argv[2]

    if schema != 'http' and schema != 'https' and schema != 'ftp':
        print('schema must be one of: http, https, ftp. %s given' % schema)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting...")

    fuse = FUSE(HttpFs(schema), mountpoint, foreground=True)
