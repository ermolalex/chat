import logging
import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="zuliprc")

# Send a channel message.
request = {
    "type": "channel",
    "to": "test",
    "topic": "tg_bot",
    "content": "I come not, friends, to steal away your hearts.",
}
result = client.send_message(request)
logging.info(result)