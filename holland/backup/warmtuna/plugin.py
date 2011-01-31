"""warmtuna backup plugin for holland"""

import os
import logging
import itertools
from holland.core import BackupPlugin, BackupError, Configspec
from holland.lib.mysql import AutoMySQLClient
from holland.backup.warmtuna.util import *

LOG = logging.getLogger(__name__)

CONFIGSPEC = """\
[warmtuna]
lock-method             = option("flush-lock", "lock-tables",
                                 default="lock-tables")
myisam-partial-indexes  = boolean(default=no)
flush-logs              = boolean(default=no)
archive-format          = option(tar, zip64, directory, default=directory)
replication-info        = boolean(default=no)

[compression]
method                  = option(gzip, default=gzip)
level                   = integer(default=1)

[mysql:client]
user                    = string()
password                = string()
host                    = string()
socket                  = string()
port                    = integer()
""".splitlines()

class WarmTuna(BackupPlugin):
    """Backup Plugin interface for warmtuna"""

    def __init__(self, name):
        self.name = name
        self.config = None

    def pre(self):
        """Setup prior to running backup

        This method can do anything useful and is generally
        used to setup a common resource potentially used
        by both estimate_size() and backup()/dryrun()
        """
        # setup client
        self.client = AutoMySQLClient(read_default_group='client', charset='utf8')
        self.datadir = self.client.show_variable('datadir')

        try:
            os.stat(os.path.join(self.datadir, 'mysql', 'user.frm'))
        except OSError:
            raise BackupError("Unable to access '%s'. "
                              "You may need to run this plugin as a more "
                              "privileged user in order to copy the raw MySQL "
                              "datadir" % self.datadir)


    def estimate(self):
        """Calculate the backup size

        This should be a best-effort guesstimate by the
        plugin at how large the final backup size will be.

        A naive plugin can simply return 0 here, but a more
        accurate estimate can be useful
        """
        size = 0
        for path in walk_datafiles(self.datadir):
            size += os.stat(path).st_size
        return size

    def backup(self):
        """Perform a backup"""
        datafiles, iterable = itertools.tee(walk_datafiles(self.datadir))
        tablenames = filenames_to_tablenames(iter_basenames(iterable), self.client)

        for path, (basename, tablename) in itertools.izip(datafiles, tablenames):
            LOG.info("Archiving %s (%s)", path, tablename)

    def dryrun(self):
        """Dry-run through the backup process"""
        datafiles, iterable = itertools.tee(walk_datafiles(self.datadir))
        tablenames = filenames_to_tablenames(iter_basenames(iterable), self.client)

        for path, (basename, tablename) in itertools.izip(datafiles, tablenames):
            LOG.info("Archiving %s (%s)", path, tablename)

    def post(self):
        """Teardown any resources configured by the plugin

        This method will be called even if backup fails, provided
        that holland itself has not been terminated
        """
        self.client.close()

    def cleanup(self):
        """Cleanup a previous backup run

        This method is called by an explicit cleanup request.
        For instance, if a snapshot was created on a previous run
        this may be called to allow the plugin to free that resource.
        """

    #@classmethod
    def configspec(cls):
        """Provide a specification for the configuration this plugin supports

        This spec can be used by external commands to generate a new
        configuration or validate an existing configuration.

        This method should return a holland.core.config.Configspec instance
        """
        return Configspec.parse(
            CONFIGSPEC
        )
    configspec = classmethod(configspec)

    #@classmethod
    def plugin_info(cls):
        return dict(
            name='warmtuna',
            summary='mysql warm backup plugin for holland',
            description='''''',
            version='1.0',
            api_version='1.1.0'
        )
    plugin_info = classmethod(plugin_info)
