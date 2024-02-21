#!/bin/bash

echo $(date) ": making bus bot rss"
cd /root/python/bus_bot
./env/bin/python print_rss.py > /var/www/static/bus_bot.xml
