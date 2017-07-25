# openqa_bugfetcher

## Installation

```sh
python3 setup.py install
```

## Configuration

You will need to configure your openQA API Key in `/etc/openqa/client.conf`:

```cfg
[openqa.opensuse.org]
key = FOO
secret = BAR
```

Then you will need to edit `/etc/openqa/bugfetcher.conf` and set up the desired openQA server
and bugtracker login information.

## Running

Just run `fetch_openqa_bugs` (you can set it up as a cron for every 10min - it will only refresh the bugs that haven't been refreshed
within the timespan configured in `bugfetcher.conf`)
