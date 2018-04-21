#! encoding=utf-8

# Creation Date: 2018-04-20 18:26:24
# Created By: Heyi Tang

from timer import Timer
import packet_tool
import config
import tool
import plottool
from datetime import datetime

if __name__ == "__main__":
    timer = Timer()
    pcaps = tool.traverse_files(config.pcap_dir, "pcap")

    for pcap in pcaps:
        data = packet_tool.load_packets(config.pcap_dir + pcap)
        timer.record("%s loaded" % pcap)

        filtered = packet_tool.filter_packets(data, config.key2ips)
        seqs = packet_tool.compute_seqs(data, filtered)
        eps_file = config.eps_dir + pcap.replace(".pcap",".eps")
        plottool.plot_seqs(seqs, fname = eps_file )
        timer.record("%s dumped" % eps_file)




