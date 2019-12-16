# FusionAuth Export/Import Commands

These python files are simple scripts that do 2 things:

1. Export the current configuration of your FusionAuth server using the API into a json file.

`python export.py --apikey {yourapikey} --url {url of your server}`

2. Apply the configuration of that saved json file to a running FusionAuth instance.

`python import.py --apikey {yourapikey} --url {url of your server} --configfile {path to exported json}`

I built these scripts as I needed a simple/repeatable way to export the configuration from my development server into production.

These scripts are extremely rough and were written for my own use. Use at your own risk.
