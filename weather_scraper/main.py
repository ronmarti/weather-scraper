import os
import requests
from datetime import date, datetime, timedelta
import pause

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class WeatherWorker(object):
    """docstring for WeatherWorker."""

    def __init__(self,
                 config: dict):
        super(WeatherWorker, self).__init__()

        # You can generate an API token from the "API Tokens Tab" in the UI
        self.influx_address = config['influx']['address']
        self.token = os.environ['INFLUXDB_ADMIN_USER_TOKEN']
        self.org = config['influx']['org']
        self.bucket = config['influx']['bucket']

        self.place = config['weather']['place']
        self.ts = timedelta(seconds=config['weather']['ts'])
        self.wurl = config['weather']['url']
        self.req_params = config['weather']['req_params']
        self.req_params['appid'] = os.environ['OPENWEATHERMAP_TOKEN']
        self.fields_to_track: list[str] = config['weather']['fields_to_track']

        self.kill = False

    def get_weather(self):
        response = requests.get(self.wurl, params=self.req_params).json()
        if response['cod'] != 401:
            selection = {
                k:v
                for k, v in response['current'].items() if k in self.fields_to_track
            }
            return response['current']['dt'], selection
        else:
            print(f'Request failed:\n{response}')
            return None, None


    
    def run_forever(self):
        next_wakeup = datetime.now()
        with InfluxDBClient(url=self.influx_address, token=self.token, org=self.org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            while(not self.kill):
                timestamp, response = self.get_weather()
                if response is None:
                    write_api.write(self.bucket, self.org, f"mem,place=Failedpl kar=0 timestamp={datetime.utcnow()}")
                    next_wakeup += self.ts
                    pause.until(next_wakeup)
                    continue
                data = [
                    f"mem,place={self.place} {k}={v} timestamp={timestamp}"
                    for k, v in response
                ]
                write_api.write(self.bucket, self.org, data)
                next_wakeup += self.ts
                pause.until(next_wakeup)
                self.kill = True

        

if __name__ == "__main__":
    import argparse
    from argparse import ArgumentParser
    from pathlib import Path
    import json

    parser = ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    path_parser = parser.add_argument('-c', '--config', type=Path, default='config.ini',
                                      help='Set path to your config.ini file.')

    args = parser.parse_args()
    if args.config.exists():
        with open(args.config, "r") as read_content:
            conf = json.load(read_content)
        worker = WeatherWorker(conf)
        worker.run_forever()
    else:
        raise argparse.ArgumentError(path_parser, f"Config file doesn't exist! Invalid path: {args.config} to config.ini.txt file, please check it!")

    print('Done')


