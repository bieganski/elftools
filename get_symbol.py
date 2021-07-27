#!/usr/bin/env python3

import subprocess
from pathlib import Path
import argparse
from typing import List, Optional, Tuple
parser = argparse.ArgumentParser(description="AAa")
parser.add_argument("--elfpath", required=True, type=Path)
parser.add_argument("--addr", required=True, type=lambda x: int(x,base=16)) # type=int doesnt work for hex

COMMAND = lambda elfpath : f"riscv-none-embed-nm -C --print-size {elfpath}"

def parse_symbols(): #  -> List:
    pass

def main(elfpath, addr):
    p = subprocess.Popen(COMMAND(elfpath), shell=True, stdout=subprocess.PIPE)

    # of form '8002066c 00000014 T _write'
    list_of_symbols = [x.decode('utf-8').rstrip('\n') for x in iter(p.stdout.readlines())]

    list_of_names = list(map(lambda line: line.split()[-1], list_of_symbols))

    # of form (addr, size): ['8002066c', '00000014']
    list_of_symbols = map(lambda line: line.split()[:2], list_of_symbols)

    def str_to_int_sanitized(addr):
        try:
            addr = int(addr, base=16)
        except:
            addr = 0x800000 # big number
        return addr
    
    # of form (addr, size): ('0x8002066c', '0x00000014')
    list_of_symbols = map(lambda addr_size: ("0x" + addr_size[0], "0x" + addr_size[1]), list_of_symbols)

    # of form (addr, size): (1234, 567)
    list_of_symbols = map(lambda addr_size: (int(addr_size[0], base=16), str_to_int_sanitized(addr_size[1])), list_of_symbols)
    
    list_of_symbols = list(list_of_symbols)

    print(len(list_of_symbols))

    res = []
    for i, (saddr, ssize) in enumerate(list_of_symbols):
        if addr >= saddr and addr < saddr + ssize:
            res.append(
                # "{:<50} {:<10} {:<10}".format
                (
                    list_of_names[i],
                    hex(saddr),
                    hex(ssize),
                )
                
            )
    
    single_res = sorted(res, key=lambda x: x[1], reverse=True)[0]

    from pprint import pprint
    pprint(single_res)
    print("===============")
    pprint(res)


main(**vars(parser.parse_args()))

