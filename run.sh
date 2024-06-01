#!/bin/bash

echo "Enter the domain name(i.e. example.com): "
read parent_domain

echo "Enter the NS IP address: "
read ns_ip

# check python3 dependency
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install python3 and try again."
    exit
fi

python3 generate.py --parent_domain $parent_domain --ns_ip $ns_ip
pytthon3 fill_ds_record.py --parent_domain $parent_domain
mkdir -p coredns_file
docker run -d -p53:53/udp -p8080:8080 -v ./coredns_config:/etc/coredns -v ./coredns_file:/var/lib/coredns --name coredns-container hjsjhn/coredns-dpt:latest
python3 break_rrsig.py