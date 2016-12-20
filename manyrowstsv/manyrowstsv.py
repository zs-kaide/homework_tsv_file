#!/usr/bin/env python
# coding:utf-8

import signal
import sys
import os
import glob
import logging
import logging.handlers
import shutil
import tempfile
import random
import datetime
import string
import click
import itertools


def write_str_into_file(
    iterable,
    output_filename,
):
    with tempfile.NamedTemporaryFile(delete=False, dir='/var/tmp',) as f:
        for row in iterable:
            f.write(row)
        shutil.move(f.name, output_filename)
    if os.path.exists(f.name):
        os.remove(f.name)


class SignalException(Exception):
    def __init__(self, message):
        super(SignalException, self).__init__(message)


def do_exit(sig, stack):
    raise SignalException("Exiting")


class TsvRowGenerator(object):

    def __init__(
        self, dt_iso_max, dt_iso_min, date_iso_max, date_iso_min,
            ):
        self.dt_iso_max = datetime.datetime.strptime(
            dt_iso_max, '%Y/%m/%d %H:%M:%S')
        self.dt_iso_min = datetime.datetime.strptime(
            dt_iso_min, '%Y/%m/%d %H:%M:%S')
        self.date_iso_max = datetime.datetime.strptime(
            date_iso_max, '%Y/%m/%d')
        self.date_iso_min = datetime.datetime.strptime(
            date_iso_min, '%Y/%m/%d')
        delta = self.dt_iso_max - self.dt_iso_min
        date_delta = self.date_iso_max - self.date_iso_min
        self.int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        self.int_date_delta = (date_delta.days * 24 * 60 * 60) + \
            date_delta.seconds

    def iterows(self):
        yield (
            "\t".join(
                ["int", "short", "long", "double", "bool",
                    "char", "utf8", "dt_iso8601", "date_iso8601"]
                ) + "\n")
        while 1:
            rdp = random.randint(0, (1 << 32) - 1)
            random_second = rdp % self.int_delta
            randomtime = self.dt_iso_min + datetime.timedelta(
                seconds=random_second)
            random_date_second = rdp % self.int_date_delta
            randomdatetime = self.date_iso_min + datetime.timedelta(
                seconds=random_date_second)
            yield ("\t".join(
                [
                    str(rdp - (1 << 31)),
                    str((rdp >> 16) - (1 << 15)),
                    str(rdp - (1 << 31)),
                    str(random.uniform(0.1, 2.7)),
                    str(rdp % 2),
                    random.choice(
                        string.ascii_letters) + random.choice(
                        string.ascii_letters) + random.choice(
                        string.ascii_letters) + random.choice(
                        string.ascii_letters),
                    u"ごんた".encode('utf-8'),
                    randomtime.strftime("%Y-%m-%d %H:%M:%S"),
                    randomdatetime.strftime("%Y-%m-%d"),
                ]) + "\n")


@click.command()
@click.argument('rows', type=int, default=1000000)
@click.option(
    '-f', '--filename',
    default="~/kadai_1.tsv",
    )
@click.option('-D', '--dt-iso-max', default="2016/12/31 00:00:00")
@click.option('-d', '--dt-iso-min', default="2016/12/1 00:00:00")
@click.option('-T', '--date-iso-max', default="2016/12/31")
@click.option('-t', '--date-iso-min', default="2016/12/1")
def cmd(rows, filename, dt_iso_max, dt_iso_min,
        date_iso_max, date_iso_min):
    LOG_MANYROWSTSV = 'logging_warning.out'
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.WARNING)
    handler = logging.handlers.RotatingFileHandler(
        LOG_MANYROWSTSV, maxBytes=2000, backupCount=5,)
    my_logger.addHandler(handler)
    s = datetime.datetime.now()
    print s + datetime.timedelta(0, 0, 0, 0, 0, 9)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGTERM, do_exit)
    try:
        write_str_into_file(
            iterable=itertools.islice(
                TsvRowGenerator(
                    dt_iso_max, dt_iso_min, date_iso_max, date_iso_min,
                ).iterows(), rows + 1),
            output_filename=os.path.abspath(os.path.expanduser(filename)),)
        print os.path.abspath(os.path.expanduser(filename))
    except SignalException as e1:
        my_logger.warning('%s: %s' % (e1, datetime.datetime.now()))
        logfiles = glob.glob('%s*' % LOG_MANYROWSTSV)
        print logfiles
        sys.exit(1)
    finally:
        e = datetime.datetime.now()
        print str(e-s)


def main():
    cmd()


if __name__ == '__main__':
    main()
