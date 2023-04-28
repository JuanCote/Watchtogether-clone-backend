from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send, join_room, leave_room, close_room


app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins=[])

rooms = dict()


@app.route('/test')
def test():
    print(id(rooms))
    return {'letssgo': 'asasasa'}


@socketio.on('disconnect')
def disconnect():
    for room in rooms:
        try:
            del rooms[room][request.sid]
            emit('leave_room', {
                'users': [user for key, user in rooms[room].items()]
            }, to=room)
        except:
            pass


# join room
@socketio.on('join_room')
def join_rooms(data):
    room = data['room']
    username = data['username']
    avatar = data['avatar']
    join_room(room)

    try:
        rooms[room].update({request.sid: [username, avatar]})
    except KeyError:
        update = {room: {request.sid: [username, avatar]}}
        rooms.update(update)

    users = [user for key, user in rooms[room].items()]
    response = {
        'resultCode': 0,
        'username': username,
        'users': users,
        'room': room,
    }
    emit('join_room', response, to=room)


@socketio.on('change_username')
def change_username(data):
    new_username = data['new_username']
    room = data['room']

    rooms[room][request.sid][0] = new_username
    users = [user for key, user in rooms[room].items()]

    emit('new_list', users, to=room)


# client disconnect
@socketio.on('client_disconnected')
def client_disconnected(data):
    username = data['username']
    room = data['room']
    leave_room(room)

    rooms[room].remove(username)

    response = {
        'resultCode': 0,
        'username': username,
        'room': room,
        'users': rooms[room]
    }

    emit('leave_room', response, to=room)


# add video to player
@socketio.on('add_video')
def add_video(data):
    username = data['username']
    room = data['room']
    url = data['url']

    response = {
        'resultCode': 0,
        'username': username,
        'room': room,
        'url': url
    }

    emit('addVideo', response, to=room)


# controller video
@socketio.on('play_video')
def play_video(data):
    username = data['username']
    room = data['room']
    action = data['action']
    seek_to = data['cur_time']

    response = {
        'resultCode': 0,
        'username': username,
        'room': room,
        'seek_to': seek_to,
        'action': action
    }

    emit('play_video', response, to=room)


# close room
@socketio.on('close_room')
def close_room(data):
    room = data['room']
    close_room(room)

    response = {
        'resultCode': 0,
    }

    send(response)


# if __name__ == "__main__":
#     socketio.run(app, port=433, allow_unsafe_werkzeug=True)
