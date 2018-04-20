#! encoding=utf-8

# Creation Date: 2018-03-27 21:19:29
# Created By: Heyi Tang

import json
import os

def json2f(data, f):
    if isinstance(data, set):
        data = list(data)
    with open(f, "w") as fout:
        json.dump(data, fout, indent = 2)

def f2json(f):
    with open(f) as fin:
        data = json.load(fin)
    return data

def traverse_files(fdir, ext, prefix = ""):
    files = []
    for f in os.listdir(fdir):
        f_full = fdir + f
        if os.path.isdir(f_full):
            files += traverse_files(f_full + "/", ext, f + "/")
        elif os.path.isfile(f_full):
            if f.split(".")[-1] == ext:
                files.append(prefix + f)
    return files
