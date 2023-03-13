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

# To start a server run a command in Server folder: uvicorn server:app

# Instantiation of a server object
sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio, static_files={
    "/": "../Client/"
})

# Instantiation of all main classes
web_object = WebAnalysis()
sqli_object = SQLAnalysis()
proxy_object = ProxyOperations()
db_object = DBControl()
global userID


# Built-in method that connects Client to a server
@sio.event
async def connect(sid, environ):
    print(sid + " connected")


# Built-in method that disconnects Client to a server
@sio.event
async def disconnect(sid):
    print(sid + " disconnected")

"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""

"""SECTION END"""
"""======================================================================================================"""
"""Database event calls to the database"""


# Checking whether user has an account
@sio.event
async def login_check(sid, data):
    user_id = db_object.check_user(data["login"], data["password"])
    if type(user_id) is int:
        return user_id
    return False


# Registering the user
@sio.event
async def register_user(sid, data):
    db_object.add_user(data["login"], data["password"])


# Returning all scans made by asking user to the
@sio.event
async def message_user_scans(sid, data):
    result = db_object.get_user_scan(data["userID"])
    return result


# Checking the result of the injection
@sio.event
async def single_result(sid, data):
    return db_object.get_result_scan(data["URL"])

"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""

"""======================================================================================================"""
"""Server-side functions in the Client-server communication"""


# Method that is responsible for the first stage of the Server
# It does: 1. Accepts user inputs 2. Processes them and runs the Server
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
        # Setting used data
        web_object.set_home_url(url)
        web_object.set_domain()
        # Using proxy or not
        if use_proxy == "Y":
            proxy_object.get_proxy_servers()
        # Collect all the links from the website
        web_object.web_crawler(level_complexity, use_proxy)
        # Sending a request to the client asking for inputs
        await sio.emit("middle_input", {
                        "links": web_object.links_w_queries,
                        "use_proxy": use_proxy,
                        "sid": sid},
                       callback=callback_middle_input, to=sid)

    # Option 2: SINGLE URL
    else:
        # Setting used data
        web_object.set_query_url(url)
        web_object.set_domain()
        # Using proxy or not
        if use_proxy == "Y":
            proxy_object.get_proxy_servers()
        # Performing the check for SQL injection
        result = sqli_object.sql_check(use_proxy)
        # Clearing lists to prevent use of needless data
        web_object.links_w_queries.clear()
        web_object.links.clear()
        # Storing the data in a new record in a database
        db_object.add_scan(userID, result)
        # Send data to the client
        await sio.emit("program_finish", {"result": result}, to=sid)


# Callback function for option 1
async def callback_middle_input(data, use_proxy, sid):
    check_list = []
    # data is a list containing indexes of links
    # Enter if user did not type in "ENTER"
    if data[0] != '':
        # Reverse the list
        for index in reversed(data):
            # if there is - sign in the element it is a range, else it is a single value
            if "-" in index:
                # Find the index of the dash
                dash = index.index("-")
                # Set the lower value for the range
                lower_value = int(index[:dash])
                # Set the upper value for the range
                upper_value = int(index[dash + 1:])
                # Extract values from the range and add them to the list of values to check
                for i in reversed(range(lower_value, upper_value + 1)):
                    check_list.append(int(i))
            else:
                check_list.append(int(index))

        # Popping URLs that were not selected by the user from the links_w_queries
        upper_value = check_list[0]
        lower_value = check_list[-1] + 1
        for i in reversed(range(lower_value, upper_value)):
            if i not in check_list:
                WebAnalysis.links_w_queries.pop(int(i))

    # Call SQL injection scanning function
    result = sqli_object.sql_check(use_proxy)
    # Clear all the excessive data from the lists for further scans
    web_object.links_w_queries.clear()
    web_object.links.clear()
    # Save records about scans in the table
    db_object.add_scan(userID, result)
    # Send result back to the user
    await sio.emit("program_finish", {"result": result}, to=sid)


"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
