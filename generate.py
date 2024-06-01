"""
DNSKEY Algorithms in RFC8624
   +--------+--------------------+-----------------+-------------------+
   | Number | Mnemonics          | DNSSEC Signing  | DNSSEC Validation |
   +--------+--------------------+-----------------+-------------------+
   | 1      | RSAMD5             | MUST NOT        | MUST NOT          |
   | 3      | DSA                | MUST NOT        | MUST NOT          |
   | 5      | RSASHA1            | NOT RECOMMENDED | MUST              |
   | 6      | DSA-NSEC3-SHA1     | MUST NOT        | MUST NOT          |
   | 7      | RSASHA1-NSEC3-SHA1 | NOT RECOMMENDED | MUST              |
   | 8      | RSASHA256          | MUST            | MUST              |
   | 10     | RSASHA512          | NOT RECOMMENDED | MUST              |
   | 12     | ECC-GOST           | MUST NOT        | MAY               |
   | 13     | ECDSAP256SHA256    | MUST            | MUST              |
   | 14     | ECDSAP384SHA384    | MAY             | RECOMMENDED       |
   | 15     | ED25519            | RECOMMENDED     | RECOMMENDED       |
   | 16     | ED448              | MAY             | RECOMMENDED       |
   +--------+--------------------+-----------------+-------------------+
"""

import os
import glob
import argparse

alg_map = {
    # 1: "RSAMD5",
    # 3: "DSA",
    5: "RSASHA1",
    # 6: "DSANSEC3SHA1",
    # 7: "RSASHA1NSEC3SHA1",
    8: "RSASHA256",
    10: "RSASHA512",
    # 12: "ECCGOST",
    13: "ECDSAP256SHA256",
    14: "ECDSAP384SHA384",
    # 15: "ED25519",
    # 16: "ED448"
}


def gen_key(domain, alg, dnskey_dir):
    print(f"Generating key for {domain} with alg {alg}")
    if alg:
        os.system(
            f"dnssec-keygen -K {dnskey_dir} -a {alg} -b 2048 -n ZONE -f KSK {domain}")
    else:
        os.system(
            f"dnssec-keygen -K {dnskey_dir} -b 2048 -n ZONE -f KSK {domain}")
    key_name = glob.glob(f"{dnskey_dir}/K{domain}*.private")[0]
    os.system(f"chmod o+r {key_name}")
    return key_name.split('/')[-1][: -8]


def get_key_name(domain, alg, dnskey_dir):
    if len(glob.glob(f"{dnskey_dir}/K{domain}*.private")):
        return glob.glob(f"{dnskey_dir}/K{domain}*.private")[0].split('/')[-1][: -8]
    else:
        return gen_key(domain, alg, dnskey_dir)


# read parent_domain and ns_ip from user
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--parent_domain", help="Parent domain name")
parser.add_argument("-n", "--ns_ip", help="NS IP")
args = parser.parse_args()
if args.parent_domain:
    parent_domain = args.parent_domain
else:
    parent_domain = input("Enter the parent domain(i.e. example.com): ")
if args.ns_ip:
    ns_ip = args.ns_ip
else:
    ns_ip = input("Enter the NS IP: ")

# NOTE: dnskey target directory must be a child directory of the current directory
root_dir = "./coredns_config"
dnskey_dir = "./coredns_config/DNSKEY"
dnskey_dir_rel = "DNSKEY"
os.makedirs(dnskey_dir, exist_ok=True)

config_dir = "./coredns_config/config"
os.makedirs(config_dir, exist_ok=True)

template_file = f"template.db"
template_command = "dnssec-keygen -K $dir -a $alg -b 2048 -n ZONE -f KSK $domain"
gen_key(parent_domain, 8, dnskey_dir)

parent_key_name = get_key_name(parent_domain, None, dnskey_dir)
output_config = f""". {{
	errors
	log
	debug
	dnssec
	health
}}

{parent_domain} {{
	file /etc/coredns/{parent_domain}.db
	dnssec {{
		key file /etc/coredns/{dnskey_dir_rel}/{parent_key_name}
	}}
	log
	errors
}}
"""

Corefile_temp = ""
with open("./Corefile.temp") as cf:
    Corefile_temp = cf.read().replace("$parent_domain", parent_domain)
with open(template_file) as f:
    template = f.read().replace("$ns_ip", ns_ip).replace(
        "$parent_domain", parent_domain)
    if not os.path.exists(f"{root_dir}/{parent_domain}.db"):
        with open(f"{root_dir}/{parent_domain}.db", "w") as of:
            of.write(template.replace("$name.", "").replace(
                "$rdata_a", "0.0.0.0"))
    for alg in alg_map:
        name = f"dnskey-alg-{alg}"
        bad_name = f"{name}-f"
        rdata_a = f"0.0.1.{alg}"
        bad_rdata_a = f"0.0.0.{alg}"

        # generate dnskey
        try:
            # print(f"dnssec-keygen -K {dnskey_dir} -a {alg} -b 2048 -n ZONE -f KSK {name}.{parent_domain}")
            key_name = get_key_name(f"{name}.{parent_domain}", alg, dnskey_dir)
            bad_key_name = get_key_name(
                f"{bad_name}.{parent_domain}", alg, dnskey_dir)
        except Exception as e:
            print(e)
            break

        # write to file
        with open(f"{config_dir}/{name}.{parent_domain}.db", "w") as of:
            of.write(template.replace("$name", name).replace(
                "$parent_domain", parent_domain).replace("$rdata_a", rdata_a))
        with open(f"{config_dir}/{bad_name}.{parent_domain}.db", "w") as of:
            of.write(template.replace("$name", bad_name).replace(
                "$parent_domain", parent_domain).replace("$rdata_a", bad_rdata_a))

        output_config += f"# {alg_map[alg]} ({alg})\n"
        output_config += Corefile_temp.replace("$name",
                                               name).replace("$key_name", key_name) + '\n'
        output_config += Corefile_temp.replace(
            "$name", bad_name).replace("$key_name", bad_key_name) + '\n'

with open(f"{root_dir}/Corefile", "w") as of:
    of.write(output_config)

# read the .key file of parent domain and print the first line that contains str "DNSKEY"
with open(f"{dnskey_dir}/{parent_key_name}.key") as f:
    for line in f.read().split('\n'):
        if "DNSKEY" in line and "IN" in line:
            print("--------------------------------------")
            print("\033[32mPlease generate DS record based on the following DNSKEY record and put it in the registrar's DNS server.\033[0m")
            print(line)
            break
