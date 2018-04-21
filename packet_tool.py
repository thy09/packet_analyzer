#! encoding=utf-8

# Creation Date: 2018-04-20 18:32:15
# Created By: Heyi Tang

from scapy.all import *
import tool

layers = ["TCP", "UDP", "HTTP", "HTTPS"]
def load_packets(f, ignore_ips = [], to_reload = False):
    json_file = f.replace(".pcap", ".json")
    if not to_reload and os.path.exists(json_file):
        return tool.f2json(json_file)
    pkt_infos = []
    for p in rdpcap(f):
        if not p.haslayer("IP"):
            continue
        ipdata = p.getlayer("IP")
        if ipdata.src in ignore_ips or ipdata.dst in ignore_ips:
            continue
        if not ipdata.haslayer("TCP") and not ipdata.haslayer("UDP"):
            continue
        sport = ipdata.payload.sport
        dport = ipdata.payload.dport
        pkt_info = {"time": p.time,
                "src": ipdata.src,
                "dst": ipdata.dst,
                "sport": sport,
                "dport": dport,
                "size": len(p),
                }
        for layer in layers:
            if p.haslayer(layer):
                pkt_info[layer] = True
        if "TCP" in pkt_info:
            if 80 in [sport, dport]:
                pkt_info["HTTP"] = True
            elif 443 in [sport, dport]:
                pkt_info["HTTPS"] = True
        pkt_infos.append(pkt_info)
    lease_time = pkt_infos[-1]["time"] - pkt_infos[0]["time"]
    start_time = pkt_infos[0]["time"]
    data = {"count": len(pkt_infos),
            "lease_time": lease_time,
            "start_time": start_time,
            "packets": pkt_infos,
            }
    tool.json2f(data, json_file)
    return data

def filter_packets(data, key2ips):
    filtered = defaultdict(lambda: defaultdict(list))
    for p in data["packets"]:
        for key, ips in key2ips.items():
            ok = False
            if p["src"] in ips:
                filtered[key]["up"].append(p)
                ok = True
            if p["dst"] in ips:
                filtered[key]["down"].append(p)
                ok = True
            if ok:
                filtered[key]["all"].append(p) 
    return filtered

def compute_bandwidth(pkts, lease_time):
    result = defaultdict(float)
    if len(pkts) < 1:
        return result
    for p in pkts:
        size = p["size"] / 1024.0
        result["total_data"] += size
        for layer in layers:
            if layer in p:
                result["%s_data" % layer] += size
    lease_time = pkts[-1]["time"] - pkts[0]["time"]
    if lease_time < 1:
        result["bandwidth"] = result["total_data"]
    else:
        result["bandwidth"] = result["total_data"] / lease_time
    for layer in layers:
        result["%s_frac" % layer] = result["%s_data" % layer] / result["total_data"]
    return result

def compute_bandwidth_for_keys(pkts_data, filtered):
    lease_time = pkts_data["lease_time"]
    result = {"_all": compute_bandwidth(pkts_data["packets"], lease_time)}
    for k, data in filtered.items():
        result[k] = compute_bandwidth(data["all"], lease_time)
    return result

def bandwidth_seqs(pkts, start_time, delta = 1.0):
    total_len = int((pkts[-1]["time"] - start_time)/delta) + 1
    bandwidths = [0.0] * total_len
    for pkt in pkts:
        ts = pkt["time"] - start_time
        bandwidths[int(ts / delta)] += pkt["size"] / 128.0
    return (map(lambda v:v*delta, range(total_len)), bandwidths)

def compute_seqs(pkts_data, filtered, delta = 1.0):
    start_time = pkts_data["start_time"]
    x, y = bandwidth_seqs(pkts_data["packets"], start_time, delta)
    seqs = [(x, y, "Total")]
    for k, data in filtered.items():
        x, y = bandwidth_seqs(data["all"], start_time, delta)
        seqs.append((x, y, k))
    return seqs
