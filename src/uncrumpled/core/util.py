'''
    Random helper utilites
'''

import os
import random
import string
from contextlib import suppress

import halt

from uncrumpled.core import dbapi

with suppress(ImportError):
    import win32file
    # Windows readlink ripped from SO lol!
    # http://stackoverflow.com/questions/27972776/having-trouble-implementing-a-readlink-function
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    FILE_READ_ATTRIBUTES = 0x0080
    OPEN_EXISTING = 3
    FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
    FILE_FLAG_BACKUP_SEMANTICS   = 0x02000000
    FILE_ATTRIBUTE_REPARSE_POINT = 0x0400

    IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003
    IO_REPARSE_TAG_SYMLINK     = 0xA000000C
    FSCTL_GET_REPARSE_POINT    = 0x000900A8
    MAXIMUM_REPARSE_DATA_BUFFER_SIZE = 0x4000

    LPDWORD = ctypes.POINTER(wintypes.DWORD)
    LPWIN32_FIND_DATA = ctypes.POINTER(wintypes.WIN32_FIND_DATAW)
    INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

    def IsReparseTagNameSurrogate(tag):
        return bool(tag & 0x20000000)

    def _check_invalid_handle(result, func, args):
        if result == INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())
        return args

    def _check_bool(result, func, args):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        return args

    kernel32.FindFirstFileW.errcheck = _check_invalid_handle
    kernel32.FindFirstFileW.restype = wintypes.HANDLE
    kernel32.FindFirstFileW.argtypes = (
        wintypes.LPCWSTR,  # _In_  lpFileName
        LPWIN32_FIND_DATA) # _Out_ lpFindFileData

    kernel32.FindClose.argtypes = (
        wintypes.HANDLE,) # _Inout_ hFindFile

    kernel32.CreateFileW.errcheck = _check_invalid_handle
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CreateFileW.argtypes = (
        wintypes.LPCWSTR, # _In_     lpFileName
        wintypes.DWORD,   # _In_     dwDesiredAccess
        wintypes.DWORD,   # _In_     dwShareMode
        wintypes.LPVOID,  # _In_opt_ lpSecurityAttributes
        wintypes.DWORD,   # _In_     dwCreationDisposition
        wintypes.DWORD,   # _In_     dwFlagsAndAttributes
        wintypes.HANDLE)  # _In_opt_ hTemplateFile

    kernel32.CloseHandle.argtypes = (
        wintypes.HANDLE,) # _In_ hObject

    kernel32.DeviceIoControl.errcheck = _check_bool
    kernel32.DeviceIoControl.argtypes = (
        wintypes.HANDLE,  # _In_        hDevice
        wintypes.DWORD,   # _In_        dwIoControlCode
        wintypes.LPVOID,  # _In_opt_    lpInBuffer
        wintypes.DWORD,   # _In_        nInBufferSize
        wintypes.LPVOID,  # _Out_opt_   lpOutBuffer
        wintypes.DWORD,   # _In_        nOutBufferSize
        LPDWORD,          # _Out_opt_   lpBytesReturned
        wintypes.LPVOID)  # _Inout_opt_ lpOverlapped

    class REPARSE_DATA_BUFFER(ctypes.Structure):
        class ReparseData(ctypes.Union):
            class LinkData(ctypes.Structure):
                _fields_ = (('SubstituteNameOffset', wintypes.USHORT),
                            ('SubstituteNameLength', wintypes.USHORT),
                            ('PrintNameOffset',      wintypes.USHORT),
                            ('PrintNameLength',      wintypes.USHORT))
                @property
                def PrintName(self):
                    dt = wintypes.WCHAR * (self.PrintNameLength //
                                           ctypes.sizeof(wintypes.WCHAR))
                    name = dt.from_address(ctypes.addressof(self.PathBuffer) +
                                           self.PrintNameOffset).value
                    if name.startswith(r'\??'):
                        name = r'\\?' + name[3:] # NT => Windows
                    return name
            class SymbolicLinkData(LinkData):
                _fields_ = (('Flags',      wintypes.ULONG),
                            ('PathBuffer', wintypes.BYTE * 0))
            class MountPointData(LinkData):
                _fields_ = (('PathBuffer', wintypes.BYTE * 0),)
            class GenericData(ctypes.Structure):
                _fields_ = (('DataBuffer', wintypes.BYTE * 0),)
            _fields_ = (('SymbolicLinkReparseBuffer', SymbolicLinkData),
                        ('MountPointReparseBuffer',   MountPointData),
                        ('GenericReparseBuffer',      GenericData))
        _fields_ = (('ReparseTag',        wintypes.ULONG),
                    ('ReparseDataLength', wintypes.USHORT),
                    ('Reserved',          wintypes.USHORT),
                    ('ReparseData',       ReparseData))
        _anonymous_ = ('ReparseData',)


def islink_win(path):
    data = wintypes.WIN32_FIND_DATAW()
    kernel32.FindClose(kernel32.FindFirstFileW(path, ctypes.byref(data)))
    if not data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT:
        return False
    return IsReparseTagNameSurrogate(data.dwReserved0)


def readlink_win(path):
    n = wintypes.DWORD()
    buf = (wintypes.BYTE * MAXIMUM_REPARSE_DATA_BUFFER_SIZE)()
    flags = FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS
    handle = kernel32.CreateFileW(path, FILE_READ_ATTRIBUTES, 0, None,
                OPEN_EXISTING, flags, None)
    try:
        kernel32.DeviceIoControl(handle, FSCTL_GET_REPARSE_POINT, None, 0,
            buf, ctypes.sizeof(buf), ctypes.byref(n), None)
    finally:
        kernel32.CloseHandle(handle)
    rb = REPARSE_DATA_BUFFER.from_buffer(buf)
    tag = rb.ReparseTag
    if tag == IO_REPARSE_TAG_SYMLINK:
        return rb.SymbolicLinkReparseBuffer.PrintName
    if tag == IO_REPARSE_TAG_MOUNT_POINT:
        return rb.MountPointReparseBuffer.PrintName
    if not IsReparseTagNameSurrogate(tag):
        raise ValueError("not a link")
    raise ValueError("unsupported reparse tag: %d" % tag)


def _create_name(page_id):
    '''
    :return: symlink name, just the page_id with extension:)
    '''
    return '{}.lnk'.format(page_id)


def rand_str(length):
    '''returns a random string of length'''
    chars = []
    for i in range(length):
        chars.append(random.choice(string.ascii_letters))
    return ''.join(char for char in chars)


def _rand_name_in_list(lst):
    '''returns a str not found in a list'''
    fname = rand_str(8)
    while fname in lst:
        fname = rand_str(8)
    return fname


def _rand_name_in_dir(dir):
    '''returns a str not found in a dir'''
    return _rand_name_in_list(os.listdir(dir))


def ufile_get(db, page_id):
    cond = "WHERE Id == '{}'".format(page_id)
    ufile = halt.load_column(db, 'Pages', ('Ufile',), cond)
    ufile = halt.load_column(db, 'Pages', ('Ufile',), cond)[0][0]
    if ufile:
        return ufile
    return False


# Generate a new file (randomly named), it's saved in the database
def ufile_create(app, page_id, init_text=None):
    fname = _rand_name_in_dir(app.notedir) + '.uncrumpled'
    dbapi.ufile_create(app.db, page_id, fname)

    with open(os.path.join(app.notedir, fname), 'w') as f:
        if init_text:
            f.write(init_text)
    return fname


def symlink(src, dst):
    if os.name == 'nt':
        try:
            win32file.CreateSymbolicLink(src, dst, 1)
        except ImportError:
            raise Exception('Please install pywin32')
    else:
        os.symlink(src, dst)


def readlink(file):
    if os.name == 'nt':
        return readlink_win(file)
    else:
        return os.readlink(file)
