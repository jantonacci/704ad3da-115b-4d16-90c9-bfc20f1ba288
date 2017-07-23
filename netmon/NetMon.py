#!/usr/bin/env python3

import ProbesLocal
import ProbesRemote
import csv
import os
from time import sleep

class Tasks(object):
    """
    Run a series of local and/or remote probes, capture results, and return them as CSV
    """
    def __init__(self, hosts=[], probes_local=[], probes_remote=[], sshclient=None):
        self.hosts = hosts
        self.probes_local = probes_local
        self.probes_remote = probes_remote
        self.sshclient = sshclient
        self.results = []
        self.failures = []
        self.csv = []

    def run(self):
        try:
            for host in self.hosts:
                for probe in self.probes_local:
                    probe_results = probe(host=host).results
                    self.results.append(probe_results)
                    if probe_results.get('returncode', 127) != 0:
                        self.failures.append(probe_results)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)
        try:
            for probe in self.probes_remote:
                probe_results = probe(sshclient=self.sshclient, host=host).results
                self.results.append(probe_results)
                if probe_results.get('returncode', 127) != 0:
                    self.failures.append(probe_results)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)

    def _results_key_set(self):
        keys = []
        for item in self.results:
            keys.extend(item)
        keys = sorted(set(keys))
        return keys

    def generate_report(self, stdout=False):
        # keys = self._results_key_set()
        keys = ['host', 'returncode', 'observation_point', 'name', 'time']

        # TODO: replace temp files with io.BytesIO object
        temp_filename = os.path.join(os.getenv('HOME', '.'), 'temp.csv')
        with open(temp_filename, 'w') as temp_filehandle:
            dict_writer = csv.DictWriter(temp_filehandle, fieldnames=keys, extrasaction='ignore', dialect='unix')
            dict_writer.writeheader()
            dict_writer.writerows(self.results)
        with open(temp_filename, 'rt') as temp_filehandle:
            for line in temp_filehandle:
                line = line.strip()
                self.csv.append(line)
                if stdout:
                    print(line)
        return self.csv


def daemon():
    """
    Run Tasks until interrupted by signal
    """
    sshclient = ProbesRemote.SshClient(host='192.168.10.128', user='netmon', passwd='n3tm0n').connect()
    tasks = Tasks(hosts=['0.0.0.0', '192.168.10.128', '192.168.10.1'],
                  probes_local=[ProbesLocal.ScanHost, ProbesLocal.ping_host],
                  probes_remote=[ProbesRemote.ScanHost, ProbesRemote.ping_host],
                  sshclient=sshclient)
    sleep_seconds = 90
    while True:
        try:
            tasks.run()
            tasks.generate_report(stdout=True)
            # print(json.dumps(tasks.results, sort_keys=True, indent=4))
            sleep(sleep_seconds)
        except KeyboardInterrupt:
            quit(0)

if __name__ == "__main__":
    daemon()