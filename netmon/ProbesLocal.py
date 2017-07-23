#!/usr/bin/env python3
import subprocess
import shlex
import json
import sys
import time
import re

class Base(object):
    """
    Runs any local command and captures results
    """
    def __init__(self, command=None, run=True, **kwargs):
        self.command = command
        self._CompletedProcess = None
        self.results = {"name": self.__class__.__name__,
                        "args": command,
                        "returncode": -1,
                        "stdout": "None",
                        "observation_point": "local_exec",
                        "time": time.time()}
        for key, value in kwargs.items():
            self.results[key] = value
        if run:
            self.run()

    def run(self):
        try:
            # subprocess.run ONLY exists in Python 3.5 or later, see README.md
            self._CompletedProcess = subprocess.run(shlex.split(self.command), stdout=subprocess.PIPE)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
        self._results_update()

    def _results_update(self):
        try:
            stdout = self._CompletedProcess.stdout.decode('UTF-8').strip()
            self.results["stdout"] = re.sub(r"( |\t)*(\n|\r\n?)( |\t)*",'', stdout)
            self.results["args"] = self._CompletedProcess.args
            self.results["returncode"] = self._CompletedProcess.returncode
            self.results["time"] = time.time()
        except Exception as err:
            # TODO: additional error handling here
            pass

    @property
    def json(self):
        try:
            return json.dumps(self.results, sort_keys=True, indent=4)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)


class PingWin(Base):
    """
    Runs ping command with correct parameters for MicroSoft Windows version
    """
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -n 3 %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)


class PingLinux(Base):
    """
    Runs ping command with correct parameters for Linux version
    """
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -c 3 %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)


def ping_host(host=None, options='', **kwargs):
    """
    Runs ping command with correct parameters for the current system
    """
    platform = sys.platform
    if platform == 'win32':
        return PingWin(host=host, options=options, platform=platform, **kwargs)
    elif platform == 'linux':
        return PingLinux(host=host, options=options, platform=platform, **kwargs)


class ScanHost(Base):
    """
    Runs NMap ping and portscan command for a single host, checks results and modifies returncode
    """
    def __init__(self, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'nmap --unprivileged -T5 -nF --open -oG - %s %s' % (options, host)
        super().__init__(command=command, host=host, **kwargs)
        if 'Status: Up' in self.results.get('stdout') or '/open/tcp//' in self.results.get('stdout'):
            self.results['returncode'] = 0
        else:
            self.results['returncode'] = 1


def example():
    """
    Run a series of remote probes as a demonstration
    """
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
    """
    Run a series of remote probes as a demonstration
    """
    example()
