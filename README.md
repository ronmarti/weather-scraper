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