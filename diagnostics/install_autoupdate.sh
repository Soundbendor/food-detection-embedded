#!/bin/bash

# Remove files from cron.daily
rm -f /etc/cron.daily/autoUpdate.sh
rm -f /etc/cron.hourly/getLogs.sh

# Cat to crontab
echo "5 4 * * * bash /home/sbcompost/food-detection-embedded/diagnostics/autoUpdate.sh" /var/spool/cron/root
echo "0 * * * * bash /home/sbcompost/food-detection-embedded/diagnostics/getLogs.sh" /var/spool/cron/root