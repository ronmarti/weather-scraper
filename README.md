# influxdb
Influx database and its hoarding of home data.

Influx:
```
admin: bitnami123
default influx token: admintoken1234
```

# Secrets
The API tokens, passwords etc. are supposed to be stored in `./secrets/.env`, which is then copied to the container on build. The app expects following content of the `.env` file:

```env
INFLUXDB_ADMIN_USER_PASSWORD=bitnami123
INFLUXDB_ADMIN_USER_TOKEN=admintoken1234
OPENWEATHERMAP_TOKEN=abcdefg123456
```
Don't forget to insert your own valid data and treat it securely.