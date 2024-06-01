import glob

# Break the RRSIG record of A record in signed zone file
print("\033[31mThis script will break the RRSIG record of A record in signed zone file.\033[0m")
print("\033[31mAll RRSIG A record key's last equal sign(=) will be removed.\033[0m")

target_signed_dir = "./coredns_file"

# NOTE: the file name is like "dnskey-alg-8-f.example.com.signed"
for file in glob.glob(f"{target_signed_dir}/*-f.*.signed"):
    output = ""
    with open(file) as f2:
        lines = f2.readlines()
        for line in lines:
            if "IN\tRRSIG\tA" in line and not line.startswith("ns"):
                output += line[:-4] + '\n'
            else:
                output += line
    with open(file, "w") as f2:
        f2.write(output)
    # print(output)
    print(
        f"RRSIG record from {file.split('/')[-1]} is successfully broken now.")
