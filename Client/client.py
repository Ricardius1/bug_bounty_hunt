import socketio
import asyncio
import requests


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""Client side"""


"""======================================================================================================"""
"""Instantiating class objects and defining basic connection functions"""

# Instantiating client object and userID and latency between server and client
sio = socketio.AsyncClient()
global userID
# In real life application this number should be higher, then there will be additional transmissions, so it will take
# longer
LATENCY = 0.5


# Function that creates connection between server and Client
@sio.event
async def connect():
    print("Connected\n")


# Print out Connection Error if it occurred
@sio.event
async def connect_error():
    print("Connection Error")


# # Function that disconnects Client from the server
@sio.event
async def disconnect():
    print("Disconnected")


"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""

"""======================================================================================================"""
"""Client Functions Accessing Database"""


@sio.event
async def log_in():
    # Asking user for their username and password
    username = input("Username: ")
    password = input("Password: ")
    # Username and password gets sent to the server to check if there is a match
    await sio.emit("login_check", {"login": username, "password": password}, callback=set_userID)
    # Wait for response
    await asyncio.sleep(LATENCY)
    # Checking the response from the server
    if type(userID) is not int:
        print("User Not Found")
        # Asking if a client wants to create an account or try again
        # Using while loop to make sure that user responded with Y or N
        while True:
            answer = input("Would you like to register?(Y, N)")
            if answer.upper() == "Y":
                await register()
                break
            elif answer.upper() == "N":
                await log_in()
                break


@sio.event
async def register():
    # Asking for username and password to register
    while True:
        username = input("Username: ")
        password = input("Password: ")
        password_rep = input("Repeat Password: ")
        if password == password_rep:
            # Sent the data to the server to create a user record in the database
            await sio.emit("register_user", {"login": username, "password": password})
            break
        else:
            print("Different passwords")


# Callback function to set a userID
async def set_userID(user_num):
    global userID
    userID = user_num


# Callback function to display the results to the user
async def display_results(data):
    print(data)

"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""

"""======================================================================================================"""
"""Client-side functions in the Client-Server communication"""


# Function that asks a user either register or log in
async def login_register():
    print("Options:\n1. Log-in\n2. Register")
    # While loop to make sure user gives correct data
    while True:
        try:
            option = int(input("Select option: "))
            # Log in form
            if option == 1:
                await log_in()
                # If user is logged in start other functions
                # This is the break case that checks if user is logged in
                if type(userID) is int:
                    break
            # Register form
            elif option == 2:
                await register()
                # After the user has registered print this and now they have to log in
                print("Options:\n1. Log-in\n2. Register")
        except ValueError:
            print("Please give a number")


# User form
@sio.event
async def program_interaction():
    print("\nUSER ACTIONS\n")
    count = 0
    # Allows user do to multiple actions during one session
    while True:
        # Print these lines every 5 times so user doesn't have to scroll up every time
        if count % 5 == 0:
            print(" 1. New Scan\n 2. Check Your Scans\n 3. Get Scan Result \n 4. Exit")
        try:
            # Ask user for actions
            option = int(input("Select Option: "))
            if option == 2:
                # Send request to the server to get all the scans done by the user
                await sio.emit("message_user_scans", {"userID": userID}, callback=display_results)
                await asyncio.sleep(LATENCY)
            elif option == 3:
                url = input("URL to check: ")
                # Send request to the server to get the result done of a specified scan
                await sio.emit("single_result", {"URL": url}, callback=display_results)
                await asyncio.sleep(LATENCY)
            elif option == 4:
                print("Program finish")
                # Disconnect from the server before exiting
                await sio.disconnect()
                exit()
            elif option == 1:
                # Start new scan
                await start_inputs()
                await sio.wait()
            count += 1
        except ValueError:
            print("Please give a number")


# Asking user for inputs needed for Server to start working
@sio.event
async def start_inputs():

    # Ask for a scan type
    print("\nChoose which type of Server do you want to run: \n1: All URLs\n2: Single URL")
    while True:
        try:
            type_of_analysis = int(input("Choose(1-2): "))
            if type_of_analysis in range(1, 3):
                break
            else:
                print("Please give correct value")
        except ValueError:
            print("Please give a number")
    # Ask for target url
    url = ""
    while True:
        # Scan all the links on the website
        if type_of_analysis == 1:
            url = input("Give target url(https://example.com/): ")
        # Scan only one link
        elif type_of_analysis == 2:
            url = input("Give target url(https://example.com/page?query): ")
            # Check that the format is right
            if "?" not in url:
                url = ""
        try:
            # If the link gets requested and if status codes is in the range ask again
            if 200 <= requests.get(url).status_code < 400:
                break
        except:
            print("Please give correct url")

    # Ask for level of complexity
    level_of_complexity = 1
    # Ask for level of complexity(how deep to scan)
    if type_of_analysis == 1:
        while True:
            try:
                level_of_complexity = int(input("Choose level of complexity(1-3): "))
                if level_of_complexity in range(1, 4):
                    break
                else:
                    print("Please give value in the specified range")
            except ValueError:
                print("Please give correct value")

    # Ask if user wants to use proxy servers
    while True:
        use_proxy = input("Do you want to use proxy(increases processing time)(Y, N)")
        use_proxy = use_proxy.upper()
        if use_proxy in ["Y", "N"]:
            break
        print("Please give only Y or N")
    print("\n")

    # Send data to the server with all inputs to start the SQLi scan
    await sio.emit("server_processes", {"type_of_analysis": type_of_analysis,
                                        "url": url,
                                        "level_of_complexity": level_of_complexity,
                                        "use_proxy": use_proxy,
                                        "userID": userID
                                        })


# Ask user for wanted URLs after sort and primary scan
@sio.event
async def middle_input(data):
    print("SELECT WANTED URLS\n")
    print("INPUT FORMAT AND RULES:")
    print("-- Values in order")
    print("-- Last index in a range is included")
    print("-- 0, 2, 4, 5   -For specific URLs")
    print("-- 0-6, 8-10  -For ranges of URLs\n")
    print("------------------------------------")
    for i, url in enumerate(data["links"]):
        print(f"{i}: {url}")
    print("------------------------------------\n")

    ALLOWED_CHAR = "0123456789-,"
    while True:
        # Asking for wanted URLs
        urls = input("Please select what URLs you want to check(press ENTER for all): ")
        no_spaces_urls = urls.replace(" ", "")
        # Check if input is correct
        if all(char in ALLOWED_CHAR for char in no_spaces_urls):
            # return the value to the callback function on the server
            return no_spaces_urls.split(","), data["use_proxy"], data["sid"]
        print("Incorrect format")


# Print out the result of user's request
@sio.event
async def program_finish(data):
    scan_list = data["result"]
    # If scan list is not empty this means that it had some positive results
    if len(scan_list) != 0:
        for res in data["result"]:
            scan_res = res[0]
            payload_link = res[1]
            if scan_res == 5:
                print(f"Very high probability in {payload_link}")
            elif scan_res == 4:
                print(f"High probability in {payload_link}")
            elif scan_res == 3:
                print(f"Medium probability in {payload_link}")
            elif scan_res == 2:
                print(f"Low probability in {payload_link}")
    # If there were no data in the list SQL was not found
    else:
        print("SQL Injection wasn't found")
    # Return to the main interface
    await program_interaction()


"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


# Function that starts the Client side functions
async def main():
    try:
        # Connect to the server
        # In real life application IP wouldn't be static and specified like this
        await sio.connect("http://localhost:8000", wait_timeout=4)
    except:
        print("Connection error, try again later")
        # TODO: use some method here to prevent from unresolved Client session message
        exit()
    # Start the program by calling login or register function
    await login_register()
    await program_interaction()
    await sio.wait()


# Start Client
if __name__ == "__main__":
    asyncio.run(main())
# TODO: find out why sometimes thee Server automatically disconnects from the server.

"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
