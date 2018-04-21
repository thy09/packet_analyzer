#! encoding=utf-8

# Creation Date: 2018-04-21 09:02:28
# Created By: Heyi Tang

import packet_tool
import tool
import config
from collections import defaultdict

if __name__ == "__main__":
    pcaps = tool.traverse_files(config.pcap_dir, "pcap")
    for pcap in pcaps:
        data = packet_tool.load_packets(config.pcap_dir + pcap)
        ip2data = defaultdict(float)
        total = 0
        for p in data["packets"]:
            ip2data[p["src"]] += p["size"]
            ip2data[p["dst"]] += p["size"]
            ips = sorted([p["src"], p["dst"]])
            ip2data["%s-%s" % (ips[0], ips[1])] += p["size"]
            total += p["size"]
        print(pcap, total / 1024.0)
        for ip, datasize in sorted(ip2data.items(), key = lambda v:v[1], reverse = True):
            if datasize < total / 10:
                break
            print(ip, datasize/1024.0)
