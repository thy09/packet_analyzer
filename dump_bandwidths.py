#! encoding=utf-8

# Creation Date: 2018-04-21 09:12:13
# Created By: Heyi Tang


from timer import Timer
import packet_tool
import config
import tool
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
        timer.record("%s started" % pcap)
        data = packet_tool.load_packets(config.pcap_dir + pcap)
        timer.record("%s loaded" % pcap)
        sheet.write(row, 0, pcap)
        sheet.write(row, 1, "Time:%.2f" % data["lease_time"])
        row += 1

        filtered = packet_tool.filter_packets(data, config.key2ips)
        result = packet_tool.compute_bandwidth_for_keys(data, filtered)
        for k, data in result.items():
            data["key"] = k
            for j, key in enumerate(keys):
                sheet.write(row, j, data.get(key))
                print(k, key, data.get(key))
            row += 1
        row += 1
        timer.record("result computed")
    xls_file = config.xls_dir + "data_%s.xls" % (datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    workbook.save(xls_file)
    timer.record("%s dumped" % xls_file)
