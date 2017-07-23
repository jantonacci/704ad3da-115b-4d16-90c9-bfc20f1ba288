#!/usr/bin/env python3

import Probes
import time
import json


class ProbeExec(object):
    def __init__(self, hosts=['localhost'], probes=[Probes.ScanHost]):
        self.hosts = hosts
        self.probes = probes
        self.results = []
        self.failures = []

    def exec_local(self):
        try:
            for host in self.hosts:
                for probe in self.probes:
                    probe_results = probe(host=host).results
                    probe_results["fn"] = "exec_local"
                    self.results.append(probe_results)
                    if probe_results.get('returncode', 0) != 0:
                        self.failures.append(probe_results)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)

    def exec_remote(self, host='localhost'):
            # Use self.results[N].get('args') to gather executed commands
            results = []
            for item in self.results:
                args = item.get('args')
                name = 'Remote%s' % item.get('name')
                # TODO: Use paramiko (SSH) for remote execution and capture results
                results.append({"fn": "exec_remote",
                                "name": name,
                                "args": args,
                                "returncode": 127,
                                "stdout": "paramiko remote exec stdout",
                                "time": time.time()})
            self.results.extend(results)


if __name__ == "__main__":
    probes = ProbeExec(hosts=['0.0.0.0', 'localhost'],
                       probes=[Probes.ScanHost, Probes.ping_host])
    probes.exec_local()
    probes.exec_remote()
    print(json.dumps(probes.results, sort_keys=True, indent=4))
