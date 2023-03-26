# Lamp editing page

Ignore splits for now.

## Header

    name: str
    instrument_name: str
    offset: int

## For each channel

    name
    value
    raw_value  # if there's a value_name

Three cases for a channel:

* No value names, no raw_value (e.g. gantom.r)
* Value names are only useful values (e.g. laser.patter)
* Value name indicate a break between regions
  * Maybe use splits?
