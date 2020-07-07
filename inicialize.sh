#!/bin/bash
echo "dtparam=spi=on" >> /boot/config.txt
echo "dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25" >>/boot/config.txt
echo "dtoverlay=spi-bcm2835-overlay" >> /boot/config.txt
