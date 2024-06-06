# Diagnostics

This folder holds the code for handling update checking and log uploading

The cronjobs for each should be as follows

```
0 */24 * * * /home/sbproto1/food-detection-embedded/diagnostics/getLogs.sh    # This will run every 24 hours on the hour
30 */1 * * * /home/sbproto1/food-detection-embedded/diagnostics/autoUpdate.sh # This will run every 30 minutes past the hour
```