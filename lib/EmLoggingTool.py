# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
# Filename: EmLoggingTool.py

'''
     Log tool for EM.
'''
import logging.handlers
import time
import gzip
import os
import re
import shutil
import GlobalModule


class Formatter(logging.Formatter):
    """
    Log formatter class.
    Modify dateFormat(datefmt).
    """

    def formatTime(self, record, datefmt=None):
        """
        Return the creation time of the specified LogRecord as formatted text.

        This method should be called from format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        in formatters to provide for any specific requirement, but the
        basic behaviour is as follows: if datefmt (a string) is specified,
        it is used with time.strftime() to format the creation time of the
        record. Otherwise, the ISO8601 format is used. The resulting
        string is returned. This function uses a user-configurable function
        to convert the creation time to a tuple. By default, time.localtime()
        is used; to change this for a particular formatter instance, set the
        'converter' attribute to a function with the same signature as
        time.localtime() or time.gmtime(). To change it for all formatters,
        for example if you want all logging times to be shown in GMT,
        set the 'converter' attribute in the Formatter class.
        """
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y/%m/%d %H:%M:%S", ct)
            s = "%s.%03d" % (t, record.msecs)
        return s


class FileHandler(logging.FileHandler):
    """
    A handler class which writes formatted logging records to disk files.
    """

    def __init__(self, filename, mode='a', encoding=None, delay=0,
                 notify_log_levels=[]):
        """
        Open the specified file and use it as the stream for logging.
        """
        logging.FileHandler.__init__(
            self, filename,  mode=mode, encoding=encoding, delay=delay)
        self.notify_log_levels = notify_log_levels

    def handle(self, record):
        """
        Call the handlers for the specified record.

        This method is used for unpickled records received from a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        super(FileHandler, self).handle(record)

        if record.levelno in self.notify_log_levels:
            snd_msg = self.format(record)
            GlobalModule.EM_LOG_NOTIFY.notify_logs(snd_msg,
                                                   record.levelno)


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, gzbackupCount=0,
                 notify_log_levels=[], gzip=False):
        logging.handlers.TimedRotatingFileHandler.__init__(
            self, filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding, delay=delay,
            utc=utc)
        self.file_name = filename
        self.gzbackupCount = gzbackupCount
        self.notify_log_levels = notify_log_levels

        self._child_handler = []
        self.gzip = gzip

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """

        super(TimedRotatingFileHandler, self).doRollover()
        for ch_handle in self._child_handler:
            ch_handle.close()
        if self.gzip:
            try:
                self._gzMake()
            except Exception:
                pass

    def getFileHandler(self):
        tmp_delay = 1 if self.stream is None else 0
        tmp_handler = FileHandler(self.baseFilename,
                                  mode=self.mode,
                                  encoding=self.encoding,
                                  delay=tmp_delay,
                                  notify_log_levels=self.notify_log_levels)
        tmp_handler.setLevel(self.level)
        self._child_handler.append(tmp_handler)
        return tmp_handler

    def _gzMake(self):
        gzip_name, gz_target_file = self._gzFilecheck()
        if gzip_name:
            self._gzFileMaker(gzip_name, gz_target_file)
        for s in self._getGzFileDeleteList():
            rm_f_path = os.path.join(os.path.dirname(self.file_name), s)
            os.remove(rm_f_path)

    def _gzFilecheck(self):
        application_log_list = self._getFile_list()
        gz_target_file_name = application_log_list[len(
            application_log_list) - 1]
        file_dir = os.path.dirname(self.file_name)
        gz_target_file = os.path.join(file_dir, gz_target_file_name)
        gzfile_name = "{0}.gz".format(gz_target_file)
        if not os.path.isfile(gz_target_file):
            gzfile_name = None
        return gzfile_name, gz_target_file

    def _gzFileMaker(self, gzfile_name, gz_target_file):
        with open(gz_target_file, 'rb') as f_in:
            with gzip.open(gzfile_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                os.remove(gz_target_file)

    def _getGzFileDeleteList(self,):
        file_list = os.listdir(os.path.dirname(self.file_name))
        base_name = os.path.basename(self.file_name)
        application_log_list = []
        delete_list = []
        for r in file_list:
            if re.search("^{0}\..*\.gz$".format(base_name), r):
                application_log_list.append(r)
        application_log_list.sort()
        if (len(application_log_list) > self.gzbackupCount
                and self.gzbackupCount != 0):
            application_log_list =\
                delete_list = application_log_list[:len(
                    application_log_list) - self.gzbackupCount]
        return delete_list

    def _getFile_list(self,):
        file_list = os.listdir(os.path.dirname(self.file_name))
        base_name = os.path.basename(self.file_name)
        new_file_list = []
        for r in file_list:
            if self._check_rotate_file(r, base_name):
                new_file_list.append(r)
        if len(new_file_list) > 0:
            new_file_list.sort()
        return new_file_list

    def _check_rotate_file(self, file_name, base_name):
        if not re.search("^{0}\.".format(base_name), file_name):
            return False
        prefix = base_name + "."
        suffix = file_name[len(prefix):]
        return_val = True if self.extMatch.match(suffix) else False
        return return_val

    def handle(self, record):
        """
        Call the handlers for the specified record.

        This method is used for unpickled records received from a socket, as
        well as those created locally. Logger-level filtering is applied.
        """
        super(TimedRotatingFileHandler, self).handle(record)

        if record.levelno in self.notify_log_levels:
            snd_msg = self.format(record)
            GlobalModule.EM_LOG_NOTIFY.notify_logs(snd_msg,
                                                   record.levelno)
