'''
    Kicks off the Boring Application stuff.
    Settuping up logging etc
'''

import os
import sys
import logging

import esky
import peasoup

import kivygui
import uncrumpled_core as core



import presenter

LOG_FILE = 'log.log'
DATABASE_FILE = 'unc.db'

class MyAppBuilder(peasoup.AppBuilder):
    def uac_bypass(self, *args, **kwargs):
        result = peasoup.AppBuilder.uac_bypass(self, *args, **kwargs)
        return self.esky_patherize(result)

# TBD I THINK ESKY HAS A FUNC THAT DOES THIS

    def esky_patherize(self, path_and_file):
        '''Don't want to get cfg files etc rewritten on new app updates!
        This moves our data file paths into the proper place
        when i find where to put data files on posix i have to change this TBD
        this runs only on portably installed stuff'''
        if not self.is_installed():
            file = path_and_file.split(os.sep)[-1]
            if hasattr(sys, 'frozen'):
                # the esky appdata holds new releases and so on our program resides in a subfolder here
                # we dump our data files and cfg files here when operating in a
                # non installed mode
                appdata_path = os.path.join(esky.util.appdir_from_executable(sys.executable),
                                            'data^-^')
                os.makedirs(appdata_path, exist_ok=True)
                return os.path.join(appdata_path, file)
            else:
                path = os.path.join(os.path.dirname(__file__), 'data^-^')
                os.makedirs(path, exist_ok=True)
                return os.path.join(path, file)

        else:
            return path_and_file

class Uncrumpled(MyAppBuilder):

    def __init__(self, *args, **kwargs):
        MyAppBuilder.__init__(self, *args, **kwargs)
        self.database_file = DATABASE_FILE

    def start(self):
        # self.hk =
        # self.tray =
        self.core = core.connect(data_dir, db=self.database_file, log=LOG_FILE)
        presenter.start(self)


DEVELOPING = True
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'developing':
        DEVELOPING = True
    if DEVELOPING:
        sys.setrecursionlimit(200)

    app_framework_instance = MyAppBuilder(main_file=MyAppBuilder.rel_path('__file__'))
    LOG_FILE = peasoup.add_date(LOG_FILE)
    LOG_FILE = app_framework_instance.uac_bypass(LOG_FILE)
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

