'''
    Kicks off the Boring Application stuff.
    Settuping up logging etc
'''
import os
from os.path import join
import sys
import logging
import shutil
import copy
from contextlib import suppress

import peasoup

import kivygui # The frontend
from uncrumpled import core
from uncrumpled.core.dbapi import create
from uncrumpled import presenter

LOG_FILE = 'log.log'
DATABASE_FILE = 'unc.db'
DEVELOPING = True

class MyAppBuilder(peasoup.AppBuilder):
    pass

class Uncrumpled(MyAppBuilder):

    def __init__(self, *args, **kwargs):
        MyAppBuilder.__init__(self, *args, **kwargs)

    def start(self):
        self.DEVELOPING = DEVELOPING
        self.data_dir = self.setup_data_dir()
        self.db = join(self.data_dir, DATABASE_FILE)
        self.notedir = join(self.data_dir, 'notes')
        os.makedirs(self.notedir, exist_ok=True)

        self.SYSTEM = copy.deepcopy(presenter.util.system_base)

        self.setup_config(self.data_dir)

        self.dev_stuff()

        if not os.path.isfile(self.db):
            logging.info('A new database is being Created')
            create.new_db(self.db)
            peasoup.set_windows_permissions(self.db)
        else:
            logging.info('Database file detected!: %s' % self.db)

        self.core = core.Core(self.db)
        self.core.DEVELOPING = self.DEVELOPING
        os.chdir(os.path.dirname(kivygui.__file__))
        self.gui = kivygui.KivyGui()
        self.gui.start(self)

    def setup_data_dir(self):
        if not DEVELOPING:
            return self.get_appdir(portable_path=os.path.dirname(__file__))
        else:
            import tempfile
            # Cleaning up the dir every time just for testing
            self.data_dir = tempfile.mkdtemp()
            cleanup = lambda: os.remove(self.data_dir)
            self.shutdown_cleanup['developing_data_dir'] = cleanup
            return self.data_dir

    def setup_config(self, data_dir):
        '''some magic done by peasoup'''
        cfg_file = join(self.data_dir, self.pcfg['config_file'])
        self.create_cfg(cfg_file)
        logging.info('First time run?: ' + str( self.first_run))

    def dev_stuff(self):
        if DEVELOPING:
            # move some files in that are required..
            path = os.path.abspath('deploy')
            required = ('default.keymap',)
            for file in required:
                shutil.copyfile(os.path.join(path, file),
                                os.path.join(self.data_dir, file))


if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'developing':
        DEVELOPING = True
    # if DEVELOPING:
        # sys.setrecursionlimit(200)

    # Setup logging in correct location
    helper = MyAppBuilder(main_file=MyAppBuilder.rel_path('__file__'))
    LOG_FILE = peasoup.add_date(LOG_FILE)
    DATA_DIR = helper.get_appdir(portable_path=
                                 os.path.realpath(os.path.dirname(__file__)),
                                 create=True)
    LOG_FILE = helper.init_file(DATA_DIR, LOG_FILE)
    peasoup.setup_logger(LOG_FILE, logging.DEBUG)

    # Exception monitoring with sentry
    if not DEVELOPING:
        with suppress(Exception):
            raven_client = peasoup.setup_raven()

    logging.info('Developer status is: %s' % DEVELOPING)
    try:
        main = Uncrumpled(main_file=MyAppBuilder.rel_path('__file__'))
        main.pcfg['log_file'] = LOG_FILE # TODO
        main.start()
    except (Exception, KeyboardInterrupt) as err:
        # main.logexception(logger=main.logger)
        if not DEVELOPING:
            with suppress(Exception):
                raven_client.captureException()
        # restarter = peasoup.Restarter()

