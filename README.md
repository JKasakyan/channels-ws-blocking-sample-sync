# Description
When a `SyncConsumer` performs a synchronous blocking action (sleep, infinite loop), all other actively connected `SyncConsumers` are blocked and subsequent connections from any `SyncConsumer` are also blocked until the blocking action is completed.

Here 'blocked' in the context of actively connected consumers means that Daphne acknowledges incoming frames from the client but no client consumer code is triggered:
> daphne.ws_protocol DEBUG WebSocket incoming frame on ['127.0.0.1', 50176]

'blocked' in the context of subsequent connections means that Channels initiates the handshake and Daphne upgrades the connection to websocket, but no client consumer code is triggered and ~5 seconds later the connection attempt times out:
> django.channels.server INFO WebSocket HANDSHAKING /ws/chat/sync [127.0.0.1:50834]
> daphne.http_protocol DEBUG Upgraded connection ['127.0.0.1', 50834] to WebSocket
> daphne.ws_protocol DEBUG WebSocket closed for ['127.0.0.1', 50834]
> django.channels.server INFO WebSocket DISCONNECT /ws/chat/sync [127.0.0.1:50834]

# Reproduction

**Prerequisites**
1. Create a new Python 3.13 virtual environment and activate it
2. Run ```pip install -r requirements.txt``` from the base of the project

**Reproducing the issue**
- Open 2 tabs, both connected to http://127.0.0.1:8000/chat/sync/, which create two `ChatSyncConsumer` instances
> django.channels.server INFO 2025-04-30 19:54:18,598 WebSocket HANDSHAKING /ws/chat/sync [127.0.0.1:58283]
> daphne.http_protocol DEBUG 2025-04-30 19:54:18,598 Upgraded connection ['127.0.0.1', 58283] to WebSocket
> chat.consumers WARNING 2025-04-30 19:54:18,599 websocket_connect in ChatSyncConsumer
> chat.consumers WARNING 2025-04-30 19:54:18,599 websocket_connect in ChatSyncConsumer
> daphne.ws_protocol DEBUG 2025-04-30 19:54:18,600 WebSocket ['127.0.0.1', 58283] open and established
> django.channels.server INFO 2025-04-30 19:54:18,600 WebSocket CONNECT /ws/chat/sync [127.0.0.1:58283]
> daphne.ws_protocol DEBUG 2025-04-30 19:54:18,600 WebSocket ['127.0.0.1', 58283] accepted by application
> django.channels.server INFO 2025-04-30 19:55:26,875 WebSocket HANDSHAKING /ws/chat/sync [127.0.0.1:58564]
> daphne.http_protocol DEBUG 2025-04-30 19:55:26,876 Upgraded connection ['127.0.0.1', 58564] to WebSocket
> chat.consumers WARNING 2025-04-30 19:55:26,877 websocket_connect in ChatSyncConsumer
> daphne.ws_protocol DEBUG 2025-04-30 19:55:26,878 WebSocket ['127.0.0.1', 58564] open and established
> django.channels.server INFO 2025-04-30 19:55:26,878 WebSocket CONNECT /ws/chat/sync [127.0.0.1:58564]
> daphne.ws_protocol DEBUG 2025-04-30 19:55:26,878 WebSocket ['127.0.0.1', 58564] accepted by application
- Confirm they are functioning by sending a test message and confirming in either the terminal or web developer console that the message was sent by the client, received by the server, and echoed back to client.
> daphne.ws_protocol DEBUG 2025-04-30 19:57:52,338 WebSocket incoming frame on ['127.0.0.1', 58283]
> chat.consumers WARNING 2025-04-30 19:57:52,340 websocket_receive in ChatSyncConsumer: {"message":"test tab 1"}
> daphne.ws_protocol DEBUG 2025-04-30 19:57:52,341 Sent WebSocket packet to client for ['127.0.0.1', 58283]
> daphne.ws_protocol DEBUG 2025-04-30 19:59:18,735 WebSocket incoming frame on ['127.0.0.1', 58564]
chat.consumers WARNING 2025-04-30 19:59:18,739 websocket_receive in ChatSyncConsumer: {"message":"test tab 2"}
daphne.ws_protocol DEBUG 2025-04-30 19:59:18,746 Sent WebSocket packet to client for ['127.0.0.1', 58564]
- In the 1st tab, type 'sleep: 60' into the input box and hit send. Confirm the following appears in the terminal:
> chat.consumers WARNING Sleeping in ChatSyncConsumer (seconds=60)
- While the 1st tab's `ChatSyncConsumer` is blocking, attempt to send another message in both tabs. The console should indicate Daphne received an incoming frame over both connections, but no consumer code will run and the message will not be returned by either consumer until the blocking `ChatSyncConsumer` completes.
> daphne.ws_protocol DEBUG 2025-04-30 20:01:22,948 WebSocket incoming frame on ['127.0.0.1', 58283]
> daphne.ws_protocol DEBUG 2025-04-30 20:01:39,912 WebSocket incoming frame on ['127.0.0.1', 58564]
> chat.consumers WARNING 2025-04-30 20:02:12,251 Awoke from sleep in ChatSyncConsumer (seconds=60)
> daphne.ws_protocol DEBUG 2025-04-30 20:02:12,253 Sent WebSocket packet to client for ['127.0.0.1', 58283]
> chat.consumers WARNING 2025-04-30 20:02:12,254 websocket_receive in ChatSyncConsumer: {"message":"test tab 2"}
> daphne.ws_protocol DEBUG 2025-04-30 20:02:12,256 Sent WebSocket packet to client for ['127.0.0.1', 58564]
> chat.consumers WARNING 2025-04-30 20:02:12,264 websocket_receive in ChatSyncConsumer: {"message":"test tab 1"}
> daphne.ws_protocol DEBUG 2025-04-30 20:02:12,265 Sent WebSocket packet to client for ['127.0.0.1', 58283]
- Repeat the sleep command in the 1st tab. While the consumer is blocking, open a new tab to attempt a new `ChatSyncConsumer` connection. The console should indicate a handshake occurs, but no consumer connection code will run and the connection will close after 5 seconds:
> django.channels.server INFO 2025-04-30 20:06:26,675 WebSocket HANDSHAKING /ws/chat/sync [127.0.0.1:61284]
> daphne.http_protocol DEBUG 2025-04-30 20:06:26,675 Upgraded connection ['127.0.0.1', 61284] to WebSocket
> daphne.ws_protocol DEBUG 2025-04-30 20:06:31,004 WebSocket closed for ['127.0.0.1', 61284]
> django.channels.server INFO 2025-04-30 20:06:31,005 WebSocket DISCONNECT /ws/chat/sync [127.0.0.1:61284]
