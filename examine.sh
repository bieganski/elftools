#!/bin/bash


SYMBOL=CAMERA_BUF_0
elf=$1

toolchain=riscv-none-embed-
# toolchain=

function find_addr {
symbol=$1
addr=`${toolchain}nm $elf | grep CAMERA_BUF_0 | cut -d ' ' -f 1`
echo $addr
}


echo "Sections present: "
${toolchain}objdump -h $elf

addr=`find_addr $SYMBOL`
echo "Address of $SYMBOL: $addr"
addr=${addr::-2}
addr=`echo $addr | sed 's/^0*//'`
echo "Trimmed address of $SYMBOL: $addr"
echo ""

${toolchain}objdump -j '.data'  -s $elf | grep --color=auto $addr
ret=$?

if ! [ $ret -eq 0 ]; then
	echo "error!"
	${toolchain}objdump -j '.sdata'  -s $elf # | grep --color=auto $addr
fi
