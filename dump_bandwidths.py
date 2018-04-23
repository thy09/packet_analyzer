#! encoding=utf-8

# Creation Date: 2018-04-21 09:12:13
# Created By: Heyi Tang


from timer import Timer
import packet_tool
import config
import tool
import xlwt
import copy
from datetime import datetime

if __name__ == "__main__":
    timer = Timer()
    pcaps = tool.traverse_files(config.pcap_dir, "pcap")
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Data")

    keys = ["key", "total_data", "bandwidth", "up_bandwidth", "down_bandwidth"]
    for layer in packet_tool.layers:
        keys.append("%s_frac" % layer)
    row = 0
    for j, key in enumerate(keys):
        sheet.write(row, j, key)
    row = 1

    ignore_ips = []
    if hasattr(config, "ignore_ips"):
        ignore_ips = config.ignore_ips
    to_reload = False
    if hasattr(config, "to_reload"):
        to_reload = config.to_reload

    for pcap in pcaps:
        timer.record("%s started" % pcap)
        data = packet_tool.load_packets(config.pcap_dir + pcap, ignore_ips = ignore_ips, to_reload = to_reload)
        timer.record("%s loaded" % pcap)
        sheet.write(row, 0, pcap)
        sheet.write(row, 1, "Time:%.2f" % data["lease_time"])
        row += 1

        max_ips = packet_tool.max_ips(data)
        key2ips = copy.deepcopy(config.key2ips)
        for ip in max_ips:
            key2ips[ip] = [ip]
        ips = ["_all"] + config.key2ips.keys() + max_ips

        filtered = packet_tool.filter_packets(data, key2ips)
        result = packet_tool.compute_bandwidth_for_keys(data, filtered)
        for k in ips:
            if not k in result:
                continue
            data = result[k]
            data["key"] = k
            for j, key in enumerate(keys):
                sheet.write(row, j, data.get(key))
                print(k, key, data.get(key))
            row += 1
        row += 1
        timer.record("result computed")
    fhead = config.pcap_dir.replace("/", "_").replace("~", "_").replace(".","_")
    xls_file = config.xls_dir + "%s_data_%s.xls" % (fhead, datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    workbook.save(xls_file)
    timer.record("%s dumped" % xls_file)
