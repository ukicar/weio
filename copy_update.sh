#!/bin/bash

# TFTP case
cp bin/ramips/openwrt-ramips-rt305x-carambola-squashfs-sysupgrade.bin /home/tftpboot/carambola.bin

# WiFi case
scp bin/ramips/openwrt-ramips-rt305x-carambola-squashfs-sysupgrade.bin root@WEIO.local:/tmp

echo "Now do in UART terminal :"
echo "root@WEIO:/# sysupgrade -v -n /tmp/openwrt-ramips-rt305x-carambola-squashfs-sysupgrade.bin"
