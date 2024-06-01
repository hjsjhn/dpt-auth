# dpt-auth
## Overview
This repository is created to set up an authoritative server for collaborating with [dpt-tool](https://github.com/hjsjhn/dpt-tool).

By simply inputting the domain name under your control (e.g., example.com) and its associated NameServer's IP address (typically the IP address of the machine running the script), you can automate the deployment of a fully-configured DNS authoritative server (using [CoreDNS](https://github.com/coredns/coredns)) with DNSSEC for the specified domain on your system. This enables the inclusion of multiple subdomains, such as `dnskey-alg-{id}.example.com` and `dnskey-alg-{id}-f.example.com`, where `id` represents the algorithm ID utilized for DNSSEC validation (see [RFC8624](https://datatracker.ietf.org/doc/html/rfc8624#section-3.1)). The '-f' suffix denotes intentional mis-signing of the DNSSEC for this subdomain.

## Usage

`./run.sh` and enter the domain name and its associated NameServer's IP address.

Make sure you have `python(>=3), docker, dnssec-keygen(come with bind9utils)` installed.

You can utilize `restart-docker.sh` to swiftly restart the CoreDNS service after making local configuration changes.