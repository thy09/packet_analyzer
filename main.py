#! encoding=utf-8

# Creation Date: 2018-04-20 18:26:24
# Created By: Heyi Tang

from timer import Timer
import packet_tool
import config
import tool
import plottool
import xlwt
from datetime import datetime

if __name__ == "__main__":
    timer = Timer()
    pcaps = tool.traverse_files(config.pcap_dir, "pcap")
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Data")

    keys = ["key", "total_data", "bandwidth"]
    for layer in packet_tool.layers:
        keys.append("%s_frac" % layer)
    row = 0
    for j, key in enumerate(keys):
        sheet.write(row, j, key)
    row = 1

    for pcap in pcaps:
        data = packet_tool.load_packets(config.pcap_dir + pcap)
        timer.record("%s loaded" % pcap)
        sheet.write(row, 0, pcap)
        sheet.write(row, 1, "Time:%.2f" % data["lease_time"])
        row += 1

        filtered = packet_tool.filter_packets(data, config.key2ips)
        seqs = packet_tool.compute_seqs(data, filtered)
        eps_file = config.eps_dir + pcap.replace(".pcap",".eps")
        plottool.plot_seqs(seqs, fname = eps_file )
        timer.record("%s plotted" % eps_file)
        result = packet_tool.compute_bandwidth_for_keys(data, filtered)
        for k, data in result.items():
            data["key"] = k
            for j, key in enumerate(keys):
                sheet.write(row, j, data.get(key))
                print(k, key, data.get(key))
            row += 1
        row += 1
        timer.record("result computed")
    workbook.save(config.xls_dir + "data_%s.xls" % (datetime.now().strftime("%Y_%m_%d_%H_%M_%S")))



