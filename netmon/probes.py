#!/usr/bin/env python3

import nmap


class HostProbes(object):
    def __init__(self, hosts=[]):
        self.nm = nmap.PortScanner()
        self.hosts = hosts

    def scan_icmp(self):
        self.nm.scan(hosts=self.hosts, arguments='-n -sP -PE -PA21,23,80,3389')

    def scan_tcp_syn(self, ports='22,3389'):
        self.nm.scan(hosts=self.hosts, arguments='-n -sP -PA%s' % ports)


if __name__ == '__main__':
    results = []

    for item in results:
        print(item)