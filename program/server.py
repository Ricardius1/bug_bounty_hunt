import time

import socketio

from web_analysis import WebAnalysis
from sql_analysis import SQLAnalysis
from proxies import ProxyOperations

sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio, static_files={
    "/": "../client/"
})


@sio.event
async def connect(sid, environ):
    print(sid + " connected")
    # sio.start_background_task(task, sid)


@sio.event
async def disconnect(sid):
    print(sid + " disconnected")
    # TODO Write code to stop the execution of the analysis process


@sio.event
async def ping(sid):
    print("ping from" + sid)

"""------------------------------------------------------------------------------------------------------------------"""


@sio.on('server_processes')
async def main(sid, data):
    # TODO: remove all comments in functions that are used in option 2
    web_object = WebAnalysis()
    sqli_object = SQLAnalysis()
    proxy_object = ProxyOperations()
    type_analysis = data['type_of_analysis']
    url = data['url']
    level_complexity = data['level_of_complexity']
    use_proxy = data['use_proxy']

    # Option 1: ALL URLs
    if type_analysis == 1:
        web_object.set_home_url(url)
        proxy_object.get_proxy_servers()
        web_object.web_crawler(level_complexity)

        # TODO: add user input for wanted pages

        result = sqli_object.sql_check(use_proxy)
        await sio.emit("response", {"result": result}, to=sid)


    # Option 2: SINGLE URL
    else:
        time_start = time.time()
        print("SERVER PT1")
        web_object.set_home_url(url)
        if use_proxy == "Y":
            proxy_object.get_proxy_servers()
        result = sqli_object.sql_check(use_proxy)
        await sio.emit("response", {"result": result}, to=sid)
        time_finish = time.time()
        print(f"Processing time: {time_finish - time_start}")
