import asyncio
import websockets


class Chatroom:
    def __init__(self, token: str, nickname: str, channel_id: str):
        self.token = token
        self.nickname = nickname
        self.channel_id = channel_id

    async def connect_chatroom(self):
        uri = "wss://irc-ws.chat.twitch.tv"
        async with websockets.connect(uri) as websocket:
            await websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
            await websocket.send(f"PASS oauth:{self.token}")
            await websocket.send(f"NICK {self.nickname}")
            await websocket.send(f"USER {self.nickname} 8 * :{self.nickname}")

            while True:
                greeting = await websocket.recv()
                if 'GLHF' in greeting:  # good luck have fun~
                    # Wait on welcome message was received
                    break
            await websocket.send(f"JOIN #{self.channel_id}")
            await asyncio.sleep(2)
            await websocket.send(f"PING :tmi.twitch.tv")
            while True:
                greeting = await websocket.recv()
