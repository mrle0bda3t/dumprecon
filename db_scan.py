import os
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from motor.motor_tornado import MotorClient
from bson import json_util
from logzero import logger


class WebpageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html")


class ChangesHandler(tornado.websocket.WebSocketHandler):

    connected_clients = set()

    def check_origin(self, origin):
        return True

    def open(self):
        ChangesHandler.connected_clients.add(self)

    def on_close(self):
        ChangesHandler.connected_clients.remove(self)

    @classmethod
    def send_updates(cls, message):
        for connected_client in cls.connected_clients:
            connected_client.write_message(message)

    @classmethod
    def on_change(cls, change):
        logger.debug(change)
        message = json_util.dumps((change['fullDocument']))
        ChangesHandler.send_updates(message)


change_stream = None


async def watch(collection):
    global change_stream

    async with collection.watch(full_document='updateLookup') as change_stream:
        async for change in change_stream:
            ChangesHandler.on_change(change)


def main():
    client = MotorClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.5.4")
    collection = client["recon"]["subdomain"]

    app = tornado.web.Application(
        [(r"/socket", ChangesHandler), (r"/", WebpageHandler)]
    )

    app.listen(3456)

    loop = tornado.ioloop.IOLoop.current()
    loop.add_callback(watch, collection)
    try:
        loop.start()
    except KeyboardInterrupt:
        pass
    finally:
        if change_stream is not None:
            change_stream.close()


if __name__ == "__main__":
    main()






# import threading
# from bson import json_util
# import pymongo
# from flask import *
# import multiprocessing
# from flask_socketio import SocketIO, emit
# import time
# import asyncio
# import socketio
# from threading import Lock
# from flask_pymongo import PyMongo



# def scan_db_changes(change_stream):
#     global mycol
#     print(str(change_stream))
#     for change in change_stream:
#         if change["operationType"] == "insert":
#            instertedFields = change['fullDocument']
#            message = json_util.dumps(instertedFields)
#            subdomain_dict = json.loads(message)
           
# def sendDataFromDb():
#     mycol = mongo.db.subdomain                 
#     user_change_stream = mycol.watch()
#     threading.Thread( target = scan_db_changes, \
#                     args = ( user_change_stream, ) ,\
#                     daemon = True ).start()
#     print("waiting for updates … ")
#     while True:
#         pass  


# if __name__ == "__main__":
#     socketio.run(app, port=4949, debug=True)



# # def scan_db_changes(change_stream):
# #     global mycol
# #     print(str(change_stream))
# #     for change in change_stream:
# #         if change["operationType"] == "insert":
# #            instertedFields = change['fullDocument']
# #            message = json_util.dumps(instertedFields)
# #            subdomain_dict = json.loads(message)
# #            print(subdomain_dict)
# #            socketio.emit('my_response',{'name':  subdomain_dict['name'], 'ip':subdomain_dict['ip'], 'port': subdomain_dict['port'], 'service': subdomain_dict['service']})

# # def sendDataFromDb():
# #     mycol = mongo.db.subdomain                     
# #     user_change_stream = mycol.watch()
# #     threading.Thread( target = scan_db_changes, \
# #                     args = ( user_change_stream, ) ,\
# #                     daemon = True ).start()
# #     print("waiting for updates … ")
# #     while True:
# #         pass  






