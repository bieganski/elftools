#!/usr/bin/env python3

from pathlib import Path

path = Path("/home/mateusz/Ikva/sw/ikva_lce/build/ikva_elf.elf")

from elftools.common.py3compat import maxint, bytes2str
from elftools.dwarf.descriptions import describe_form_class
from elftools.elf.elffile import ELFFile


def process_file(filename, address=None, funcname=None):
    print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()

        if address is not None:
            funcname = decode_funcname(dwarfinfo, address)
            file, line = decode_file_line(dwarfinfo, address)
        else:
            assert funcname is not None
            symtab = elffile.get_section_by_name('.symtab')
            assert symtab is not None

            # Test we get all expected instances of the symbol '$a'.
            syms = symtab.get_symbol_by_name(funcname)
            assert len(syms) == 1
            address = syms[0].entry.st_value
            print(type(address))

            funcname = bytes(funcname, 'latin-1') # for compatilibility with 'decode_file_line' function
            file, line = decode_file_line(dwarfinfo, address)

        print('Function:', bytes2str(funcname))
        print('File:', bytes2str(file))
        print('Line:', line)


from pprint import pprint

def decode_funcname(dwarfinfo, address):
    # Go over all DIEs in the DWARF information, looking for a subprogram
    # entry with an address range that includes the given address. Note that
    # this simplifies things by disregarding subprograms that may have
    # split address ranges.
    res = []
    for CU in dwarfinfo.iter_CUs():
        for DIE in CU.iter_DIEs():
            # print(DIE)
            try:
                if DIE.tag == 'DW_TAG_subprogram':
                    # print(DIE)
                    lowpc = DIE.attributes['DW_AT_low_pc'].value

                    # DWARF v4 in section 2.17 describes how to interpret the
                    # DW_AT_high_pc attribute based on the class of its form.
                    # For class 'address' it's taken as an absolute address
                    # (similarly to DW_AT_low_pc); for class 'constant', it's
                    # an offset from DW_AT_low_pc.
                    highpc_attr = DIE.attributes['DW_AT_high_pc']
                    highpc_attr_class = describe_form_class(highpc_attr.form)
                    # pprint(DIE.attributes)
                    if highpc_attr_class == 'address':
                        highpc = highpc_attr.value
                    elif highpc_attr_class == 'constant':
                        highpc = lowpc + highpc_attr.value
                    else:
                        print('Error: invalid DW_AT_high_pc class:',
                              highpc_attr_class)
                        continue

                    if lowpc <= address <= highpc:
                        name = DIE.attributes['DW_AT_name'].value
                        res.append(name)
                        # print(name)
                        # return DIE.attributes['DW_AT_name'].value
            except KeyError:
                continue
    if len(res) != 1:
        print("==== WARNING: found more than one matching value!")
        from pprint import pprint
        pprint(res)
        print(f"==== Returning {res[0]}")
    res = res[0]
    return res


def decode_file_line(dwarfinfo, address):
    # Go over all the line programs in the DWARF information, looking for
    # one that describes the given address.
    for CU in dwarfinfo.iter_CUs():
        # First, look at line programs to find the file/line for the address
        lineprog = dwarfinfo.line_program_for_CU(CU)
        prevstate = None
        for entry in lineprog.get_entries():
            # We're interested in those entries where a new state is assigned
            if entry.state is None:
                continue
            if entry.state.end_sequence:
                # if the line number sequence ends, clear prevstate.
                prevstate = None
                continue
            # Looking for a range of addresses in two consecutive states that
            # contain the required address.
            if prevstate and prevstate.address <= address < entry.state.address:
                filename = lineprog['file_entry'][prevstate.file - 1].name
                line = prevstate.line
                return filename, line
            prevstate = entry.state
    return None, None



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str)
    parser.add_argument('--addr', type=lambda x : int(x, 16))
    parser.add_argument('--path', type=Path, required=True)
    args = parser.parse_args()
    path = args.path
    if args.symbol is None and args.addr is None:
        raise ValueError("Error: please pass either --symbol or --addr params!")
    if args.addr:
        process_file(path, address=args.addr)
    else:
        process_file(path, funcname=args.symbol)
