# 704ad3da-115b-4d16-90c9-bfc20f1ba288
**_ATTENTION_**: Requires Python 3.5 due to subprocess.run dependency in ProbesLocal.py class Base, which as the name implies is the 'base' for everything. Sorry. Yes, I could re-write it with subprocess.Popen, but that re-write is a very low priority.

## Objective
Given a list of hosts, verify availability (with a high degree of confidence through multiple local and remote probe types and methods), then return a report.

## Method
Nmap is a free Security Scanner, Port Scanner, & Network Exploration Tool.
