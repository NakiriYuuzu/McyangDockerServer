import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class GroupConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        self.room_group_name = 'group'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data=None, type='receive'):
        to_json = json.dumps(text_data)
        result = json.loads(to_json)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': result['message'],
                'TeamDesc_id': result['TeamDesc_id'],
                'Identity': result['Identity'],  # 0 = Teacher 1 = Student
                'Leader': result['Leader'],
                'Member': result['Member']
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'TeamDesc_id': event['TeamDesc_id'],
            'Identity': event['Identity'],
            'Leader': event['Leader'],
            'Member': event['Member']
        }))


class RaceStudentConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        self.room_group_name = 'studentRace'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data=None, type='receive'):
        to_json = json.dumps(text_data)
        result = json.loads(to_json)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': result['message'],
                'Race_id': result['Race_id']
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'Race_id': event['Race_id']
        }))


class RaceConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data=None, type='receive'):
        to_json = json.dumps(text_data)
        result = json.loads(to_json)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': result['message'],
                'Race_id': result['Race_id']
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'Race_id': event['Race_id']
        }))


class SignConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        self.room_group_name = 'sign'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data=None, type='receive'):
        to_json = json.dumps(text_data)
        result = json.loads(to_json)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': result['message'],
                'Sign_id': result['Sign_id']
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'Sign_id': event['Sign_id']
        }))


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    def connect(self):
        self.room_group_name = 'chat'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def receive(self, text_data=None, type='receive'):
        to_json = json.dumps(text_data)
        result = json.loads(to_json)
        # this for web
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': result['message'],
                'cid': result['cid']
            }
        )

    def chat_message(self, event):
        data = event['message']

        print(data)

        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': data,
            'cid': event['cid']
        }))
