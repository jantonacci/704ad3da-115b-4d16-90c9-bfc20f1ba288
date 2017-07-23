#!/usr/bin/env python3

import re
import time
import paramiko
import json
import shlex


class AttributeAccumulator(object):
    """
    Replicates subprocess.CompletedProcess for paramiko.command_exec, similar to ProbesLocal.Base
    """
    pass

class SshClient(object):
    """
    Establish a single SSH client connection to the remote system for use by all probes
    """
    def __init__(self, host=None, port=22, user=None, passwd=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        #self._key = key  # public key auth not implemented
        self.session = None

    def connect(self):
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(paramiko.WarningPolicy())  # Development Only
            # self.session.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Development Only
            # self.session.set_missing_host_key_policy(paramiko.RejectPolicy())  # Production
            self.session.load_system_host_keys()
            self.session.connect(self.host, self.port, self.user, self.passwd)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
        return self.session

class Base(object):
    """
    Replicates ProbesLocal.Base for remote probes, runs any command
    """
    def __init__(self, sshclient=None, command=None, run=True, **kwargs):
        if not isinstance(sshclient, paramiko.SSHClient):
            raise TypeError('type paramiko.SSHClient required as parameter sshclient, not %s' % type(sshclient))
        self.sshclient = sshclient
        self.command = command
        self._CompletedProcess = AttributeAccumulator()
        self.results = {"name": self.__class__.__name__,
                        "args": command,
                        "returncode": -1,
                        "stdout": "None",
                        "observation_point": "remote_exec",
                        "time": time.time()}
        for key, value in kwargs.items():
            self.results[key] = value
        if run:
            self.run()

    def run(self):
        try:
            # http://docs.paramiko.org/en/latest/api/
            stdout = self.sshclient.exec_command(self.command)[1]
            self._CompletedProcess.returncode = stdout.channel.recv_exit_status()
            self._CompletedProcess.stdout = stdout.read()
            self._CompletedProcess.args = shlex.split(self.command)
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


class PingLinux(Base):
    """
    Ping on Linux requires parameters to terminate, other wise runs continuously
    """
    def __init__(self, sshclient=None, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'ping -c 3 %s %s' % (options, host)
        super().__init__(sshclient=sshclient, command=command, host=host, **kwargs)


def ping_host(sshclient=None, host=None, options='', **kwargs):
    """
    Replicates ProbesLocal.ping_host, but always returns PingLinux - here for compatibility
    """
    return PingLinux(sshclient=sshclient, host=host, options=options, platform='linux', **kwargs)


class ScanHost(Base):
    """
    Runs NMap ping and portscan command for a single host, checks results and modifies returncode
    """
    def __init__(self, sshclient=None, host=None, options='', **kwargs):
        self._host = host
        self.metainfo = {"category": "returncode", "type": int}
        command = 'nmap --unprivileged -T5 -nF --open -oG - %s %s' % (options, host)
        super().__init__(sshclient=sshclient, command=command, host=host, **kwargs)
        if 'Status: Up' in self.results.get('stdout') or '/open/tcp//' in self.results.get('stdout'):
            self.results['returncode'] = 0
        else:
            self.results['returncode'] = 1


def example():
    """
    Run a series of remote probes as a demonstration
    """
    sshclient = SshClient(host='192.168.10.128', user='netmon', passwd='n3tm0n').connect()
    results = [Base(sshclient=sshclient, command='ls -lA')]

    results.append(ScanHost(sshclient=sshclient, host='0.0.0.0'))
    results.append(ping_host(sshclient=sshclient, host='0.0.0.0'))
    results.append(ScanHost(sshclient=sshclient, host='localhost'))
    results.append(ping_host(sshclient=sshclient, host='localhost'))

    for item in results:
        # print(item.results)
        print(item.json)


if __name__ == '__main__':
    """
    Run a series of remote probes as a demonstration
    """
    example()
