# Bus bot

Telegram bot to notify when seats are available on a bus.

## Requests

List of requests for the information we need

| API | Description | Used by | URL | Query Parameters? | Notes |
| --- | --- | --- | --- | --- | --- |
| eligible_journeys | Get journeys for pass ID | [Rides page] | <https://app.zeelo.co/api/travels/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/elegible-journey-groups>|❌||
| stops | Get stops | [Rides page] | <https://app.zeelo.co/api/stops/by_id?page=1&per_page=25>|❌||
| journeys | Get journeys | [Pass page] | <https://app.zeelo.co/api/travel-passes/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/eligible-journey-groups>|✅||
| capacity | Get capacity | [Pass page] | <https://app.zeelo.co/api/journeys/capacity_between_stops>|❌||

[Rides page]: https://app.zeelo.co/rides/jlr
[Pass page]: https://app.zeelo.co/my-zeelo/travel-pass/38u1fj13-rfd8-q99a-ap22-ao92929ifikf

## Journeys URL parameters

| Parameter | Description | Example |
| --- | --- | --- |
| product_id | Product ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| origin_stop_id[] | Origin stop ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| destination_stop_id[] | Destination stop ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |
| tier_id[] | Tier ID | 38u1fj13-rfd8-q99a-ap22-ao92929ifikf |

### Example URL

<https://app.zeelo.co/api/travel-passes/38u1fj13-rfd8-q99a-ap22-ao92929ifikf/eligible-journey-groups?product_id=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&origin_stop_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&destination_stop_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf&tier_id[]=38u1fj13-rfd8-q99a-ap22-ao92929ifikf>

## Requirements

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.11.1  |

## Commands

### Set up environment

```bash
python -m venv env
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python ./bot.py
```

## Telegram credentials

To obtain an access token for telegram, see [help page](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API), but in essence, talk to the [BotFather](https://t.me/botfather).

The access token is used via an environment variable, or a `.env` file, which is not tracked by git.

Also in the environment should be an "admin ID", where errors are sent via the error handler.

```bash
touch .env
```

```.env
TELEGRAM_BOT_ACCESS_TOKEN=...
ADMIN_USER_IDS=...
```

## Persistent data

To store each user's preferred stops and reminder preference, a persistent pickle file is used. This is not tracked by git. This uses the [Persistence API](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Making-your-bot-persistent) from [python-telegram-bot][ptb].

[ptb]: https://github.com/python-telegram-bot/python-telegram-bot/

```python
persistent_data = PicklePersistence(filepath="bot_data.pickle")
application = Application.builder().token(API_KEY).persistence(persistent_data).build()
```

## Deploy on remote server

### Set up environment on server

```bash
ssh server
mkdir -p /usr/alifeee
cd /usr/alifeee
git clone https://github.com/alifeee/bus_bot.git
cd bus_bot
sudo apt-get update
sudo apt install python3.10-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
echo {} >> historical_capacities.json
# create user
sudo adduser --system --no-create-home --group bus_bot
sudo chown -R alifeee:bus_bot .
chmod g=rw historical_capacities.json
chmod g=rw bot_data.pickle
```

### Move over secrets

```bash
scp google_credentials.json server:/env/alifeee/bus_bot/
scp .env server:/usr/alifeee/bus_bot/
```

### Run bot

```bash
ssh server
cd /usr/alifeee/bus_bot
cp bus_bot.service /etc/systemd/system/bus_bot.service
sudo systemctl enable bus_bot.service
sudo systemctl start bus_bot.service
sudo systemctl status bus_bot.service
```

### Update

```bash
ssh server
cd /usr/alifeee/bus_bot
git pull
```

Then repeat steps in [Run](#run-bot)
