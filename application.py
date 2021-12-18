# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
from github import Github
# new
import time
import os, sys, time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    # one way to fetch single line-wise
    # doesnt fetch all the lines at once if already present
    # cur = 0
    # while True:
    #     try:
    #         with open('text.txt') as f:
    #             f.seek(0,2)
    #             if f.tell() < cur:
    #                 f.seek(0,0)
    #             else:
    #                 f.seek(cur,0)
    #             for line in f:
    #                 print(line.strip())
    #                 socketio.emit('newnumber', {'number': line.strip()}, namespace='/test')
    #                 socketio.sleep(5)
    #             cur = f.tell()
    #     except IOError:
    #         pass
    #     time.sleep(1)

    # another way to read all at once and then read one by one
    name = "text.txt"
    current = open(name, "r")
    curino = os.fstat(current.fileno()).st_ino
    while True:
        while True:
            buf = current.read(1024)
            if buf == "":
                break
            sys.stdout.write(buf.strip())
            socketio.emit('newnumber', {'number': buf.strip()}, namespace='/test')
            socketio.sleep(5)
        try:
            if os.stat(name).st_ino != curino:
                new = open(name, "r")
                current.close()
                current = new
                curino = os.fstat(current.fileno()).st_ino
                continue
        except IOError:
            pass
        time.sleep(1)

    # while not thread_stop_event.isSet():
    #     # First create a Github instance:

    #     # using an access token
    #     # g = Github("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")
    #     # repo = g.get_repo("lavsharmaa/sample-test")
    #     # contents = repo.get_contents("README.md")
    #     # # Then play with your Github objects:
    #     # print(contents)
    #     # socketio.emit('newnumber', {'number': contents}, namespace='/test')
    #     # socketio.sleep(5)

    #     number = round(random()*10, 3)
    #     print(number)
    #     socketio.emit('newnumber', {'number': number}, namespace='/test')
    #     socketio.sleep(5)


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
