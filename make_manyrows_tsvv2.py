# coding:utf-8

import signal
import os
import stat
import codecs
import shutil
import tempfile
import random
import datetime
import string
from StringIO import StringIO
import click


def do_exit(sig, stack):
    raise Exception("Exiting")


def make_manyrows(
        fpath, temp, rows, dt_iso_max, dt_iso_min,
        date_iso_max, date_iso_min):
    chunk = 500  # 分割ブロック
    delta = dt_iso_max - dt_iso_min
    date_delta = date_iso_max - date_iso_min
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    int_date_delta = (date_delta.days * 24 * 60 * 60) + date_delta.seconds
    # 日時の範囲で差をとり、その値をランダムに変更することで作成している。
    try:
        fd = codecs.open(temp, "wb", "utf-8")
        fd.write(u"\t".join(
            ["int", "short", "long", "double", "bool",
                "char", "utf8", "dt_iso8601", "date_iso8601"]) + u"\n")
        output = StringIO()
        n = 0
        for i in xrange((rows // chunk) + 1):
            if rows >= (i+1) * chunk:
                ch = chunk
            elif rows % chunk:
                ch = rows % chunk
            else:
                break
            # print float(i) / ((rows // chunk) + 1)
            # print multiprocessing.current_process().name, rows
            strings = ""
            for h in xrange(ch):
                rdp = random.randint(0, (1 << 32) - 1)
                random_second = rdp % int_delta
                randomtime = dt_iso_min + datetime.timedelta(
                    seconds=random_second)
                random_date_second = rdp % int_date_delta
                randomdatetime = date_iso_min + datetime.timedelta(
                    seconds=random_date_second)
                strings += u"\t".join(
                    [
                        unicode(rdp - (1 << 31)),
                        unicode((rdp >> 16) - (1 << 15)),
                        unicode(rdp - (1 << 31)),
                        unicode(random.uniform(0.1, 2.7)),
                        unicode(rdp % 2),
                        unicode(random.choice(
                            string.ascii_letters) + random.choice(
                            string.ascii_letters) + random.choice(
                            string.ascii_letters) + random.choice(
                            string.ascii_letters)),
                        unicode(u"ごんた"),
                        unicode(randomtime.strftime("%Y-%m-%d %H:%M:%S")),
                        unicode(randomdatetime.strftime("%Y-%m-%d")),
                    ]) + u"\n"
                n += 1
            output.write(strings)
            if n % 100000 == 0:
                fd.write(output.getvalue())
                output.close()
                output = StringIO()
            # 1000000を越えるとStringIOを解放する。
        fd.write(output.getvalue())
        shutil.move(temp, fpath)
    except Exception as e1:
        print e1, "srgs"
    finally:
        output.close()
        fd.close()


@click.command()
@click.argument('rows', type=int, default=100000000)
@click.option(
    '-f', '--fpath',
    default="/vagrant/work/magori_kadai/kadai_2/kadai_v1.tsv",
    )
@click.option('-D', '--dt-iso-max', default=u"2016/12/31 00:00:00")
@click.option('-d', '--dt-iso-min', default=u"2016/12/1 00:00:00")
@click.option('-T', '--date-iso-max', default=u"2016/12/31")
@click.option('-t', '--date-iso-min', default=u"2016/12/1")
def cmd(rows, fpath, dt_iso_max, dt_iso_min,
        date_iso_max, date_iso_min):
    s = datetime.datetime.now()
    print s + datetime.timedelta(0, 0, 0, 0, 0, 9)
    signal.signal(signal.SIGINT, do_exit)
    signal.signal(signal.SIGHUP, do_exit)
    signal.signal(signal.SIGTERM, do_exit)

    fd, temp = tempfile.mkstemp()
    os.close(fd)
    os.chmod(temp, stat.S_IRWXU | stat.S_IROTH)
    try:
        dt_iso_max = datetime.datetime.strptime(
            dt_iso_max, u'%Y/%m/%d %H:%M:%S')
        dt_iso_min = datetime.datetime.strptime(
            dt_iso_min, u'%Y/%m/%d %H:%M:%S')
        date_iso_max = datetime.datetime.strptime(
            date_iso_max, u'%Y/%m/%d')
        date_iso_min = datetime.datetime.strptime(date_iso_min, u'%Y/%m/%d')
        make_manyrows(
            fpath, temp, rows, dt_iso_max, dt_iso_min,
            date_iso_max, date_iso_min
        )
    except Exception as e2:
        print e2
    finally:
        if os.path.exists(temp):
            os.remove(temp)
        e = datetime.datetime.now()
        print str(e-s)


def main():
    cmd()


if __name__ == '__main__':
    main()
