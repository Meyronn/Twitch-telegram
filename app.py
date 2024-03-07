# Standard library imports
import logging
import time
import traceback

# Third party imports
import requests
import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Logger settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


channel_id = "-1001234567890" # your channel id where will be sended the alert
bot_token = "1234567890:AAH_whatimdoingw1thmylife" # your bot token from @BotFather

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

settings = {
    'twitch': {
        'channel': 'hikkikomoa', # Inserter your channel name 
        'client_id': 'insert your client_id', # Client id from https://dev.twitch.tv/console/extensions
        'client_secret': 'insert your secret key', # Secret key from https://dev.twitch.tv/console/extensions in the settings of the extension
        'access_token': None # Access token will be generated automatically
    }
}

previous_stream_state = None 

# Automatically generate access token
def refresh_access_token():
    response = requests.post(
        'https://id.twitch.tv/oauth2/token',
        data={
            'client_id': settings['twitch']['client_id'],
            'client_secret': settings['twitch']['client_secret'],
            'grant_type': 'client_credentials'
        }
    )
    if response.status_code == 200:
        response_json = response.json()
        settings['twitch']['access_token'] = response_json['access_token']
        logger.info(f"{time.strftime('%H:%M:%S', time.localtime())} | Access token updated: {response_json['access_token']}")
    else:
        logger.error(f"Error updating access token: {response.status_code}")

# Checking stream activity status
async def check_stream_status():
    global previous_stream_state

    response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={settings['twitch']['channel']}",
                            headers={
                                'Client-ID': settings['twitch']['client_id'],
                                'Authorization': 'Bearer ' + settings['twitch']['access_token']
                            }
                            )
    if response.status_code == 200:
        data = response.json()
        if len(data['data']) > 0:
            current_stream_state = True
        else:
            current_stream_state = False

        if current_stream_state != previous_stream_state:
            if current_stream_state:
                message = "Stream started!"
                logger.info(f"{time.strftime('%H:%M:%S', time.localtime())} | {message}")
                await send_message_to_telegram(message)
            else:
                message = "Stream ended!"
                logger.info(f"{time.strftime('%H:%M:%S', time.localtime())} | {message}")
                await send_message_to_telegram(message)

            previous_stream_state = current_stream_state
    else:
        tb=traceback.format_exc()
        logger.error(f'Error when requesting stream data: {response.status_code}\n{tb}')


# Sending message to the telegram channel
async def send_message_to_telegram(message):
    try:
        await bot.send_message(channel_id, message)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error sending a message to Telegram: {e}\n{tb}")

async def main():
    logger.info("Bot succesfully launched!.")
    while True:
        if not settings['twitch']['access_token']:
            refresh_access_token()
        else:
            await check_stream_status() 
        await asyncio.sleep(3)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    executor.start_polling(dp, skip_updates=True)
