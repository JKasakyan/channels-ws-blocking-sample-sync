import json
import logging
from time import sleep

from channels.consumer import SyncConsumer

logger = logging.getLogger(__name__)


class ChatSyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        logger.warning('websocket_connect in %s', self.__class__.__name__)
        self.send({
            "type": "websocket.accept",
        })

    def websocket_disconnect(self, event):
        logger.warning('websocket_disconnect in %s', self.__class__.__name__)

    def websocket_receive(self, event):
        logger.warning('websocket_receive in %s: %s', self.__class__.__name__, event['text'])
        text_data_json = json.loads(event['text'])
        message = text_data_json['message']
        if 'loop' in message:
            logger.warning('Starting infinite loop in %s', self.__class__.__name__)
            while True:
                pass
        if 'sleep:' in message:
            try:
                seconds = int(message.split(':')[-1])
            except Exception:
                logger.warning('Using fallback of 10 seconds')
                seconds = 10
            logger.warning('Sleeping in %s (seconds=%s)', self.__class__.__name__, seconds)
            sleep(seconds)
            logger.warning('Awoke from sleep in %s (seconds=%s)', self.__class__.__name__, seconds)
        self.send({
            "type": "websocket.send",
            "text": event["text"],
        })
