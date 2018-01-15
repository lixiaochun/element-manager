# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2017 Nippon Telegraph and Telephone Corporation
# Filename: EmCommonLog.py

'''
Log tool for EM.
'''
import logging.handlers
import time


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


class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False):
        logging.handlers.TimedRotatingFileHandler.__init__(
            self, filename, when=when, interval=interval,
            backupCount=backupCount, encoding=encoding, delay=delay, utc=utc)
        self._child_handler = []

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

    def getFileHandler(self):
        tmp_delay = 1 if self.stream is None else 0
        tmp_handler = logging.FileHandler(self.baseFilename,
                                          mode=self.mode,
                                          encoding=self.encoding,
                                          delay=tmp_delay)
        self._child_handler.append(tmp_handler)
        return tmp_handler
