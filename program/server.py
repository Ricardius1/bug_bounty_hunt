import socketio

from web_analysis import WebAnalysis
from sql_analysis import SQLAnalysis
from proxies import ProxyOperations
from db_class import DBControl


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""Server side"""


"""======================================================================================================"""
"""Instantiating class objects and defining basic connection functions"""

# To start a server run a command in program folder: uvicorn server:app

# Instantiation of a server object
sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio, static_files={
    "/": "../client/"
})

# Instantiation of all main classes
web_object = WebAnalysis()
sqli_object = SQLAnalysis()
proxy_object = ProxyOperations()
db_object = DBControl()


# Built-in method that connects client to a server
@sio.event
async def connect(sid, environ):
    print(sid + " connected")


# Built-in method that disconnects client to a server
@sio.event
async def disconnect(sid):
    print(sid + " disconnected")


"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


@sio.event
async def login_check(sid, data):
    user_id = db_object.check_user(data["login"], data["password"])
    if type(user_id) is int:
        return user_id
    return False


@sio.event
async def register_user(sid, data):
    db_object.add_user(data["login"], data["password"])


@sio.event
async def message_user_scans(sid, data):
    print("Message received")
    result = db_object.get_user_scan(data["userID"])
    print(result)
    return result


@sio.event
async def single_result(sid, data):
    result = db_object.get_result_scan(data["URL"])
    return result


"""======================================================================================================"""
"""Server-side functions in the client-server communication"""


# Method that is responsible for the first stage of the program
# It does: 1. Accepts user inputs 2. Processes them and runs the program
@sio.on('server_processes')
async def main(sid, data):

    # Assigning user inputs
    type_analysis = data['type_of_analysis']
    url = data['url']
    level_complexity = data['level_of_complexity']
    use_proxy = data['use_proxy']
    global userID
    userID = data["userID"]

    # Selecting which type of analysis user chose

    # Option 1: ALL URLs
    if type_analysis == 1:
        web_object.set_home_url(url)
        web_object.set_domain()
        # Using proxy or not
        if use_proxy == "Y":
            proxy_object.get_proxy_servers()
            # TODO add more proxy suppliers because sometimes there are no https servers
        web_object.web_crawler(level_complexity, use_proxy)

        await sio.emit("middle_input", {
                        "links": web_object.links_w_queries,
                        "use_proxy": use_proxy,
                        "sid": sid},
                       callback=callback_middle_input, to=sid)

    # Option 2: SINGLE URL
    else:
        web_object.set_query_url(url)
        web_object.set_domain()
        if use_proxy == "Y":
            proxy_object.get_proxy_servers()
        result = sqli_object.sql_check(use_proxy)
        db_object.add_scan(userID, result)
        await sio.emit("program_finish", {"result": result}, to=sid)


async def callback_middle_input(data, use_proxy, sid):
    if data[0] != '':
        for index in reversed(data):
            if "-" in index:
                dash = index.index("-")
                lower_value = int(index[:dash])
                upper_value = int(index[dash+1:])
                for i in reversed(range(lower_value, upper_value + 1)):
                    WebAnalysis.links_w_queries.pop(i)
            else:
                WebAnalysis.links_w_queries.pop(int(index))
    result = sqli_object.sql_check(use_proxy)
    db_object.add_scan(userID, result)
    await sio.emit("program_finish", {"result": result}, to=sid)



"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
