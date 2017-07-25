# 704ad3da-115b-4d16-90c9-bfc20f1ba288
**_ATTENTION_**: Requires Python 3.5 due to subprocess.run dependency in ProbesLocal.py class Base, which as the name implies is the 'base' for everything. Sorry. Yes, I could re-write it with subprocess.Popen, but that re-write is a very low priority.

## Objective
Given a list of hosts, verify availability (with a high degree of confidence through multiple local and remote probe types and methods), then return a report.

## Method
Nmap is a free Security Scanner, Port Scanner, & Network Exploration Tool. Using the pyton subprocess module, Nmap is run locally to verify a host is available.  Using the python paramiko module, Nmap can scan the same host from a second 'observation point' to independently verify the locally captured results.

## Issues
As written, this does not scale. Nmap can quickly scan entire subnets when used directly.  However, as implemented, only one host at a time is scanned in order to make parsing the results and modifying the return code simple. Additionally, the local and remote probes are run in sequence when they should/could be run in parallel.
