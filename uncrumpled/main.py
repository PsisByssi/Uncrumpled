'''
    Kicks off the Boring Application stuff.
    Settuping up logging etc
'''

import os
from os.path import join
import sys
import logging

import esky
import peasoup

import kivygui
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
        self.data_dir = self.setup_data_dir()
        self.db = os.path.join(self.data_dir, DATABASE_FILE)
        # self.hk =
        # self.tray =
        # self.hk = system_hotkey.SystemHotkey(consumer=self.hotkey_consumer,
                                             # check_queue_interval=0.001)
        self.setup_config(self.data_dir)

        if not os.path.isfile(self.db):
            logging.info('A new database is being Created')
            create.new_db(self.db)
            peasoup.set_windows_permissions(self.db)
        else:
            logging.info('Database file detected!: %s' % self.db)

        os.chdir(os.path.dirname(kivygui.__file__))
        self.core = core.Core(self.db)
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
        cfg_file = os.path.abspath(join(self.data_dir, self.pcfg['config_file']))
        self.create_cfg(cfg_file)
        logging.info('First time run?: ' + str( self.first_run))



if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'developing':
        DEVELOPING = True
    if DEVELOPING:
        sys.setrecursionlimit(200)

    app_framework_instance = MyAppBuilder(main_file=MyAppBuilder.rel_path('__file__'))
    LOG_FILE = peasoup.add_date(LOG_FILE)
    DATA_DIR = app_framework_instance.get_appdir(portable_path=os.path.realpath(os.path.dirname(__file__)), create=True)
    LOG_FILE = app_framework_instance.init_file(DATA_DIR, LOG_FILE)
    peasoup.setup_logger(LOG_FILE)
    if not DEVELOPING:
        with suppress(Exception):
            raven_client = peasoup.setup_raven()
    logging.info('Developer status is: %s' % DEVELOPING)

    try:
        main = Uncrumpled(main_file=MyAppBuilder.rel_path('__file__'))
        # THIS NEEDS TO BE SAVED!  DISGUSTING MAN...
        main.pcfg['log_file'] = LOG_FILE
        main.start()
    except (Exception, KeyboardInterrupt) as err:
        main.logexception(logger=main.logger)
        # if not DEVELOPING:
        #     with suppress(Exception):
        #         raven_client.captureException()

        restarter = peasoup.Restarter()

        if not DEVELOPING:
            with suppress(Exception):
                raven_client.captureException()

