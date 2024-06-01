#!/bin/bash

# check python3 dependency
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install python3 and try again."
    exit
fi

# check dnssec-keygen dependency
if ! command -v dnssec-keygen &> /dev/null
then
    echo "dnssec-keygen is not installed. Please install bind9utils and try again."
    exit
fi

# check docker dependency
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install docker and try again."
    exit
fi

echo "Enter the domain name(i.e. example.com): "
read parent_domain

echo "Enter the NS IP address: "
read ns_ip

python3 generate.py --parent_domain $parent_domain --ns_ip $ns_ip
python3 fill_ds_record.py --parent_domain $parent_domain
mkdir -p coredns_file
chmod 777 coredns_file
docker run -d -p53:53/udp -p8080:8080 -v $(realpath ./coredns_config):/etc/coredns -v $(realpath ./coredns_file):/var/lib/coredns --name coredns-container hjsjhn/coredns-dpt:latest

while [ ! "$(ls -A ./coredns_file/)" ]; do
    echo "Waiting for DNSSEC signing..."
    sleep 3
done
sleep 1

python3 break_rrsig.py