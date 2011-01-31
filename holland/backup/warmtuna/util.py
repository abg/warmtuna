"""Utility methods for warmtuna"""

import os
import glob

def walk_datafiles(datadir):
    # '*.{frm,MYD,MYI,MRG,TRG,TRN,ARM,ARZ,opt,par}'
    join = os.path.join
    patterns = [
        # metadata
        join('*', '*.opt'),
        join('*', '*.frm'),
        # MyISAM
        join('*', '*.MYD'),
        join('*', '*.MYI'),
        join('*', '*.MRG'), # (merge tables)
        # Triggers
        join('*', '*.TRG'),
        join('*', '*.TRN'),
        # Archive
        join('*', '*.ARM'),
        join('*', '*.ARZ'),
        # partitions
        join('*', '*.par')
    ]

    for pattern in patterns:
        path_pattern = join(datadir, pattern)
        for path in glob.glob(path_pattern):
            yield path

def iter_basenames(iterable):
    for path in iterable:
        name = os.path.basename(path)
        name, ext = os.path.splitext(name)
        yield name

def filenames_to_tablenames(names, client):
    """Convert a MySQL 5.1 filename to its utf8 tablename"""
    cursor = client.cursor()
    for name in names:
        cursor.execute('SELECT CONVERT(_filename%s USING UTF8)', name)
        yield name, cursor.fetchone()[0]
    cursor.close()
