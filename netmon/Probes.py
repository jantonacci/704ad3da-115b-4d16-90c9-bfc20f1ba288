#!/usr/bin/env python3
import subprocess
import shlex
import json
import sys
import time

class Base(object):
    def __init__(self, command=None, run=True, **kwargs):
        self.command = command
        self._CompletedProcess = None
        self.results = {"name": self.__class__.__name__,
                        "args": shlex.split(command),
                        "returncode": 127,
                        "stdout": "None",
                        "time": time.time()}
        for key, value in kwargs.items():
            self.results[key] = value
        if run:
            self.run()

    def run(self):
        try:
            self._CompletedProcess = subprocess.run(shlex.split(self.command), stdout=subprocess.PIPE)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
        self.results["args"] = self._CompletedProcess.args,
        self.results["returncode"] = self._CompletedProcess.returncode,
        self.results["stdout"] = self._CompletedProcess.stdout.decode('UTF-8')
        self.results["time"] = time.time()

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


class PingLinux(Base):
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -c 3 %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)


def ping_host(host=None, options='', **kwargs):
    platform = sys.platform
    if platform == 'win32':
        return PingWin(host=host, options=options, platform=platform, **kwargs)
    elif platform == 'linux':
        return PingLinux(host=host, options=options, platform=platform, **kwargs)


class ScanHost(Base):
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'nmap --unprivileged -T5 -nF --open -oG - %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)
        if 'Status: Up' in self.stdout:
            self.results['returncode'] = 0
        else:
            self.results['returncode'] = 1


def example():
    results = []
    platform = sys.platform
    if platform == 'win32':
        results = [Base(command='cmd.exe /c dir')]
    elif platform == 'linux':
        results = [Base(command='ls -lA')]

    results.append(ScanHost(host='0.0.0.0'))
    results.append(ping_host(host='0.0.0.0'))
    results.append(ScanHost(host='localhost'))
    results.append(ping_host(host='localhost'))

    for item in results:
        # print(item.results)
        print(item.json)


if __name__ == '__main__':
    example()
