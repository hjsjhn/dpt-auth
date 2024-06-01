import argparse
import glob
import os

target_signed_dir = "./coredns_file"
os.makedirs(target_signed_dir, exist_ok=True)

# set argparse arguments --parent_domain(-d)
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--parent_domain", help="Parent domain name")
args = parser.parse_args()
if args.parent_domain:
    parent_domain = args.parent_domain
else:
    parent_domain = input("Enter the parent domain(i.e. example.com): ")
parent_domain_config = f"./{parent_domain}.db"

# open parent_domain_config and append content
with open(parent_domain_config, "a") as f:
    f.write('\n\n')
    for file in glob.glob(f"{target_signed_dir}/*.signed"):
        with open(file) as f2:
            f.write(f"; DS record from {file.split('/')[-1]}\n")
            lines = f2.readlines()
            for line in lines:
                if "IN\tCDS" in line:
                    f.write(line.replace("IN\tCDS", "IN\tDS"))
            f.write("\n")
        print(f"Filled DS record from {file.split('/')[-1]}")
