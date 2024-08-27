#!/bin/bash

# Remove files from cron.daily
rm -f /etc/cron.daily/autoUpdate.sh
rm -f /etc/cron.hourly/getLogs.sh

# Cat to crontab
echo "5 4 * * * /home/sbcompost/food-detection-embedded/diagnostics/autoUpdate.sh" >>/var/spool/cron/crontabs/root
echo "0 * * * * /home/sbcompost/food-detection-embedded/diagnostics/getLogs.sh" >>/var/spool/cron/crontabs/root
