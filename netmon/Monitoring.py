#!/usr/bin/env python3

import Probes


class ProbesLocal(object):
    def __init__(self, hosts=['localhost'], probes=[Probes.ScanHost]):
        self.hosts = hosts
        self.probes = probes
        self.results = []
        self.failures = []
        try:
            for host in self.hosts:
                for probe in self.probes:
                    probe_results = probe(host=host).results
                    self.results.append(probe_results)
                    if probe_results.get('returncode', 0) != 0:
                        self.failures.append(probe_results)
        except Exception as err:
            # TODO: additional error handling here
            raise Exception(err)


if __name__ == "__main__":
    probes = ProbesLocal(hosts=['0.0.0.0', 'localhost'],
                         probes=[Probes.ScanHost, Probes.ping_host])
    for result in probes.failures:
        print(result)
