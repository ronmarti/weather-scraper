import os
import requests
from datetime import date, datetime, timedelta, timezone
import pause

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from rx import catch


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

        self.place = config['openweathermap']['place']
        self.ts = timedelta(seconds=config['openweathermap']['ts'])
        self.openweather_url = config['openweathermap']['url']
        self.openweather_req_params = config['openweathermap']['req_params']
        self.openweather_req_params['appid'] = os.environ['OPENWEATHERMAP_TOKEN']
        self.fields_to_track: list[str] = config['openweathermap']['fields_to_track']

        self.weatherapi_url = config['weatherapi']['url']
        self.weatherapi_req_params = config['weatherapi']['req_params']
        self.weatherapi_req_params['key'] = os.environ['WEATHERAPI_TOKEN']

        self.ibc_url = config['ibc']['url']
        self.ibc_req_params = config['ibc']['req_params']
        self.ibc_req_params['apiKey'] = os.environ['IBC_TOKEN']

        self.kill = False

    def get_openweathermap(self):
        response = requests.get(self.openweather_url, params=self.openweather_req_params).json()
        if response['cod'] != 401:
            selection = {
                k:v
                for k, v in response['current'].items() if k in self.fields_to_track
            }
            # return response['current']['dt'], selection
            now = round(1e9*datetime.now(timezone.utc).timestamp())  # in nanoseconds
            return now, selection
        else:
            print(f'Request failed:\n{response}')
            return None, None

    def get_weatherapi(self):
        response = requests.get(self.weatherapi_url, params=self.weatherapi_req_params).json()

    def get_ibc(self, date: datetime = None):
        if date is None:
            date = datetime.today()
        self.ibc_req_params['date'] = datetime.strftime(date, '%y-%m-%d')
        response = requests.get(self.ibc_url, params=self.ibc_req_params).json()
        unwrapped = {
            round(1e6*pair[0]): pair[1]
            for pair in response['chartData']['data'] if pair[1] is not None
        }
        return unwrapped

    
    def run_forever(self):
        next_wakeup = datetime.now()
        with InfluxDBClient(url=self.influx_address, token=self.token, org=self.org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            while(not self.kill):
                try:
                    now = round(1e9*datetime.now(timezone.utc).timestamp())
                    response_ibc = self.get_ibc()
                    [
                        write_api.write(self.bucket, self.org,f"ibc power={v} {k}")
                        for k, v in response_ibc.items()
                    ]
                    # write_api.write(self.bucket, self.org, data_ibc)

                    timestamp, response = self.get_openweathermap()
                    if response is None:
                        write_api.write(self.bucket, self.org, f"mem,place=Failedpl kar=0 {now}")
                        next_wakeup += self.ts
                        pause.until(next_wakeup)
                        continue
                    data = [
                        f"mem,place={self.place} {k}={v} {timestamp}"
                        for k, v in response
                    ]
                    write_api.write(self.bucket, self.org, data)
                except Exception as exc:
                    print(exc)
                    print('Will try again in the next iteration...')
                next_wakeup += self.ts
                pause.until(next_wakeup)
                # self.kill = True

        

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


