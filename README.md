# Example Project for Weather Logging
Influx database and its hoarding of home data and [OpenWeatherMap](https://openweathermap.org) current data.

Note that, openweathermap API updates values each 10 mins, not faster. The free API is limited to 60 calls/minute.


# Secrets
The API tokens, passwords etc. are supposed to be stored in `./secrets/.env`, which is then copied to the container on build. The app expects following content of the `.env` file:

```env
INFLUXDB_ADMIN_USER_PASSWORD=bitnami123
INFLUXDB_ADMIN_USER_TOKEN=admintoken1234
OPENWEATHERMAP_TOKEN=abcdefg123456
```
Don't forget to insert your own valid data and treat it securely.

# Influx Frontend
Access the GUI on `http://localhost:8086/` when influx container is running.
```
admin: bitnami123
```

## Influx Address
If you are running the scraper outside of the Docker-compose, you have to take care of the IP adresses of the InfluxDB in the `configs/config.json` under the entry `influx.address`. E.g., on the localhost, put there 
```json
...
"address": "http://127.0.0.1:8086",
...
```
whereas when inside docker-compose networking, there will be address of `"address": "http://influx-container-name:8086"`.