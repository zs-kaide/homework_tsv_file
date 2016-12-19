#!/usr/bin/env python
# coding:utf-8

import signal
import sys
import os
import glob
import logging
import logging.handlers
import csv
import shutil
import tempfile
import datetime
import click
import pickle
import struct


class ParseRowsTsv(object):

    def __init__(
        self, inputf, outputf
            ):
        self.inputf = os.path.abspath(os.path.expanduser(inputf))
        self.outputf = os.path.abspath(os.path.expanduser(outputf))

    def read_tsv(self):
        with open(self.inputf, "rb") as f:
            reader = csv.reader(f, delimiter="\t", lineterminator='\n')
            yield reader.next()
            for row in reader:
                row = (
                    int(row[0]),
                    int(row[1]),
                    int(row[2]),
                    float(row[3]),
                    int(row[4]),
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                )
                yield row

    def pickle_tsv(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            for record in self.read_tsv():
                pickle.dump(record, f)
            shutil.move(f.name, self.outputf)
        if os.path.exists(f.name):
            os.remove(f.name)

    def struct_tsv(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            lines = self.read_tsv()
            line = lines.next()
            inits = struct.Struct(
                's '.join(
                    [str(len(line[i])) for i in range(9)]) + 's')
            f.write(inits.pack(*line))
            for record in lines:
                s = struct.Struct(
                    'i h l d ? %ds %ds %ds %ds' % (
                        len(record[5]), len(record[6]),
                        len(record[7]), len(record[8]),
                        )
                    )
                f.write(s.pack(*record))
            shutil.move(f.name, self.outputf)
        if os.path.exists(f.name):
            os.remove(f.name)


class SignalException(Exception):
    def __init__(self, message):
        super(SignalException, self).__init__(message)


def do_exit(sig, stack):
    raise SignalException("Exiting")


@click.command()
@click.option(
    '--file', type=click.Choice(['pickle', 'struct']),
    default='pickle')
@click.option('-i', '--inputf', default='~/kadai_1.tsv')
@click.option('-o', '--outputf', default='~/kadai_2.p')
def cmd(file, inputf, outputf):
    s = datetime.datetime.now()
    print s + datetime.timedelta(0, 0, 0, 0, 0, 9)
    # シグナル
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGTERM, do_exit)
    # ログハンドラーを設定する
    LOG_MANYROWSTSV = 'logging_warning.out'
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.WARNING)
    handler = logging.handlers.RotatingFileHandler(
        LOG_MANYROWSTSV, maxBytes=2000, backupCount=5,)
    my_logger.addHandler(handler)

    parser = ParseRowsTsv(inputf, outputf)
    try:
        if file == 'pickle':
            parser.pickle_tsv()
        elif file == 'struct':
            parser.struct_tsv()

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
