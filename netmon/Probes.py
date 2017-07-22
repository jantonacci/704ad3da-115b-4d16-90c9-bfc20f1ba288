#!/usr/bin/env python3
import subprocess
import shlex
import json
import sys


class Base(object):
    def __init__(self, command=None, **kwargs):
        self.name = self.__class__.__name__
        self.command = command
        try:
            self._CompletedProcess = subprocess.run(shlex.split(command), stdout=subprocess.PIPE)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
        self.results = {"name": self.name,
                        "args": self._CompletedProcess.args,
                        "returncode": self._CompletedProcess.returncode,
                        "stdout": self._CompletedProcess.stdout.decode('UTF-8')}
        for key, value in kwargs.items():
            self.results[key] = value

    @property
    def args(self):
        return self._CompletedProcess.args

    @property
    def json(self):
        try:
            return json.dumps(self.results, sort_keys=True, indent=4)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
    @property
    def returncode(self):
        return self._CompletedProcess.returncode

    @property
    def stdout(self):
        return self._CompletedProcess.stdout.decode('UTF-8')


class PingWin(Base):
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -n 3 %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)

class PingPosix(Base):
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -c 3 %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)

def PingHost(host=None, options='', **kwargs):
    platform = sys.platform
    if platform == 'win32':
        return PingWin(host=host, options=options, platform=platform, **kwargs)
    elif platform == 'posix':
        return PingPosix(host=host, options=options, platform=platform, **kwargs)

class ScanHost(Base):
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'nmap --unprivileged -T5 -nF --open -oG - %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)

    @property
    def returncode(self):
        if 'Status: Up' in self.stdout:
            return 0
        return 1


if __name__ == '__main__':
    results = [# Base(command='cmd.exe /c dir /w'),
               ScanHost(host='0.0.0.0'),
               PingHost(host='0.0.0.0'),
               ScanHost(host='localhost'),
               PingHost(host='localhost')]

    for item in results:
        # print(type(item))
        # print(dir(item))
        print(item.json)
