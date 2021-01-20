# Python API client for fetching Plaato data

Fetches data for the Plaato Keg and Plaato Airlock using the official API handed by [blynk.cc](blynk.cc)

To be able to query the API an `auth_token` is required and which can be obtained by following [these](https://plaato.zendesk.com/hc/en-us/articles/360003234717-Auth-token) instructions

For more information about the available pins that can be retrieved please see the official [docs](https://plaato.zendesk.com/hc/en-us/articles/360003234877-Pins) from Plaato

## Usage
```
usage: cli.py [-h] -t AUTH_TOKEN -d {keg,airlock,both} [-u URL] [-k API_KEY]

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -t AUTH_TOKEN         Auth token received from Plaato
  -d {keg,airlock}

optional arguments:
  -u URL                Mock url
  -k API_KEY            Header key for mock url
```

## Available pins

### Keg
```python
    BEER_NAME = "v64"
    PERCENT_BEER_LEFT = "v48"
    POURING = "v49"
    BEER_LEFT = "v51"
    BEER_LEFT_UNIT = "v74"
    TEMPERATURE = "v56"
    UNIT_TYPE = "v71"
    MEASURE_UNIT = "v75"
    MASS_UNIT = "v73"
    VOLUME_UNIT = "v82"
    LAST_POUR = "v59"
    DATE = "v67"
    OG = "v65"
    FG = "v66"
    ABV = "v68"
    FIRMWARE_VERSION = "v93"
    LEAK_DETECTION = "v83"
    MODE = "v88"
```

### AirLock
```python
    BPM = "v102"
    TEMPERATURE = "v103"
    BATCH_VOLUME = "v104"
    OG = "v105"
    SG = "v106"
    ABV = "v107"
    TEMPERATURE_UNIT = "v108"
    VOLUME_UNIT = "v109"
    BUBBLES = "v110"
    CO2_VOLUME = "v119"
```

### Disclaimer
This python library was not made by Plaato. It is not official, not developed, and not supported by Plaato.
