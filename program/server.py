import socketio


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio, static_files={
    "/": "../client/"
})


@sio.event
async def connect(sid, environ):
    print(sid + " connected")
    sio.start_background_task(task, sid)


@sio.event
async def disconnect(sid):
    print(sid + " disconnected")


@sio.event
async def task(sid):
    await sio.sleep(5)
    # This is where the function mult was called from, so here you will receive a callback
    # Accept it and pass to the function that will process it
    # In our case func is called cb, and it prints the result of the callback

    # await sio.emit("mult", {'numbers': [3, 4]}, callback=cb)

    # Instead of this function we can use
    result = await sio.call("mult", {'numbers': [3, 4]}, to=sid)
    print(result)


@sio.event
async def sum(sid, data):
    result = data['numbers'][0] + data['numbers'][1]

    # This is a way how to send data back from the server by creating a new event
    # await sio.emit("sum_result", {"result": result}, to=sid)

    # Second option is doing this on the server side
    return result


@sio.event
async def message(sid, msg):
    print(msg)
