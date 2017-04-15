import os
from os.path import join
from sys import platform

import requests
from plumbum import cmd

LINUX = True if 'linux' in platform else False

def zsh_run(msg, file, *args):
    # logger.info('appimage: ' + msg)
    path = join(os.path.dirname(__file__), file)
    if args:
        cmd.zsh(path, *args)
    else:
        cmd.zsh(path)

# a+x for chmod
# FIXME python3 only
A_X = 0o777

def dl_and_save(name ,url):
    r = requests.get(url)
    with open(name, 'wb') as file:
        file.write(r.content)

def get_apprun():
    dl_and_save('AppRun',
                'https://github.com/probonopd/AppImageKit/releases/download/continuous/AppRun-x86_64')
    os.chmod('AppRun', A_X)

def generate_appimage(app_name, version, arch):
    file = 'AppImageAssistant'
    dl_and_save(file,
                'https://github.com/probonopd/AppImageKit/releases/download/6/AppImageAssistant_6-x86_64.AppImage')
    os.chmod(file, A_X)

    out_dir = join(os.pardir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    out_file = join(out_dir, app_name+'-'+version+'-x86_64.AppImage')
    try:
        os.remove(out_file)
    except FileNotFoundError:
        pass

    print('finazlizing this shit')
    zsh_run('finalizing appimage', 'finalize_appimage.zsh', version, name, arch)


import os, shutil, sys
from os.path import join
from pprint import pprint as pp
from pybuilder.core import use_plugin, init, task, depends

use_plugin("python.core")
use_plugin('copy_resources')

# use_plugin("python.unittest")
use_plugin("python.install_dependencies")
# use_plugin("python.flake8")
# use_plugin("python.coverage")

@init
def init_wget(project):
    project.plugin_depends_on("plumbum")

name = "uncrumpled"
version = "0.1.0"
# default_task = "publish"
default_task = "appimage"

@init
def set_properties(project):
    project.depends_on('pyyaml')
    project.depends_on('yamlordereddictloader')
    project.depends_on('psutil')
    project.depends_on('peasoup')
    project.depends_on('appdirs')
    project.depends_on('tkquick')
    project.depends_on('Pillow')
    project.depends_on('halt')
    project.depends_on('timstools')
    project.depends_on('piefuzz')
    project.depends_on('system_hotkey') # TODO this dep sohuld autopull in deps
                                        # http://python-packaging.readthedocs.io/en/latest/dependencies.html
    if LINUX:
        project.depends_on('xcffib')
         # TODO tmp pypi package, until an offical one comes out https://github.com/BurntSushi/xpybutil/issues/10
        project.depends_on('uncrumpled_xpybutil')

    # kivygui deps
    project.depends_on('uncrumpled_kivygui')
    # https://kivy.org/docs/installation/installation-linux.html
    project.depends_on('Cython')
    project.depends_on('uncrumpled_kivy') # TODO recycleboxlayout not included in kivy pypi...
    # TODO tmp pypi package https://github.com/reclosedev/async_gui/issues/6
    project.depends_on('uncrumpled_async_gui')

    project.set_property("dir_source_main_python", "src/uncrumpled")
    project.set_property("dir_source_unittest_python", "test")
    project.set_property("dir_source_main_scripts", "src/scripts")

    project.set_property("appimage_arch", "x86-64")

@init
def init_appimage(project):
    project.plugin_depends_on("virtualenv")
    # project.plugin_depends_on("plumbum")

    # a script file to start it all off
    project.set_property_if_unset("main_entry_point", project.name)
    # project.set_property_if_unset("appimage_pyver", "3.5")
    # can be relative to basedire or absolute, MUST be png, preferably 256x256
    project.set_property_if_unset("appimage_force", False)
    project.set_property_if_unset("appimage_icon", "/usr/share/icons/hicolor/256x256/apps/logview.png")
    project.set_property_if_unset("appimage_arch", "i686")

@task
@depends('package')
def appimage(project, logger):
    from plumbum import cmd, local

    arch = project.get_property("appimage_arch")
    # TODO make the 32 or 64 be valid input options (easier)
    assert arch in ('i686', 'x86-64', 'armv6l')

    name_lower = name.lower()
    p_output = project.expand_path("$dir_target")
    appimgdir = join(p_output, "appimage", name+version, 'in' , name+'.AppDir')
    try:
        os.makedirs(appimgdir, exist_ok=False)
    except FileExistsError:
        print()
        print('Appimage dir already exists for version {}, overwrite (y/N)'.format(version))

        force = project.get_property('appimage_force')
        if force in (True, "1", "True", "true"):
            logger.warn("appimage: overwriting as appimage_force is True")
            # Delete the entire "in" folder
            shutil.rmtree(os.path.dirname(appimgdir))
            os.makedirs(appimgdir, exist_ok=False)
        # Prompt to overwrite or not
        else:
            ans = input()
            if ans in ('y', 'Y'):
                # Delete the entire "in" folder
                shutil.rmtree(os.path.dirname(appimgdir))
                os.makedirs(appimgdir, exist_ok=False)
            elif ans in ('n', 'N', ''):
                logger.info('appimage: nothing done')
                raise Exception
            else:
                logger.warning('appimage: Expected either y or n, recieved: ' + ans)
                raise Exception
    # pyver = 'python{}.{}'.format(sys.version_info.major,
                                # sys.version_info.minor)
    os.chdir(appimgdir)
    # with local.cwd(appimgdir):
    shutil.rmtree('usr', ignore_errors=True)
    logger.info('appimage: creating virtualenv in AppDir')
    cmd.virtualenv('usr')
        # os.makedirs('usr/share/pyshared')
        # root_site_packages = '/usr/lib/'
        # os.makedirs('usr/lib/'+pyver'/site-packages')
        # site_packages =
        # for p in site.getsitepackages():
            # if 'site-packages' in p:
                # site_packages = p
                # break
        # else:
            # raise Exception('site packages not found...')

    # TODO make a flag to use existing venv or a new one..
    # will probably fail if we have development libs installed with pip install -e
    logger.info('appimage: Installing python libraries')
    pip = local['usr/bin/pip']
    for dep in project.dependencies:
        logger.info('appimage: installing dep: '+str(dep))
        # TODO look how pybuilder installs deps...
        pip['install', dep]()

    logger.info('appimage: Copy our pybuilder bundled app into the appdir')
    src = project.expand_path('$dir_dist')
    shutil.copytree(src, join(appimgdir, name_lower))

    # TODO can we reorganize our projecet so that this isn't necessary?
    # Installs our own projet using pip -install -e
    src_setup = join(project.basedir,
                     os.path.dirname(project.get_property("dir_source_main_python")),
                     'setup.py')
    dst_setup = join(appimgdir, 'setup.py')
    shutil.copy(src_setup, dst_setup)
    pip['install', '-e', appimgdir]()

    # TODO insert bangline for correct python version
    logger.info('appimage: create symlink to script files')
    script_dir = join(name_lower, 'scripts')
    for script in os.listdir(script_dir):
        file = join(script_dir, script)
        pointing_to = join(os.pardir, os.pardir, file)
        if os.path.isfile(file):
            os.symlink(pointing_to, 'usr/bin/' + script)
            os.chmod(file, A_X)

    with open(join(appimgdir, name_lower+'.desktop'), 'w') as f:
        data = ('[Desktop Entry]',
                'Name='+name,
                'Exec='+project.get_property('main_entry_point'),
                'Icon='+name_lower)
        f.write('\n'.join(data))

    logger.info('appimage: moving in files')
    cmd.cp(project.get_property('appimage_icon'), name_lower+'.png')

    logger.info('appimage: getting apprun')
    get_apprun()

    os.chdir(os.pardir)

    logger.info('appimage: getting/running AppImageAssistant')
    generate_appimage(name, version, arch)


