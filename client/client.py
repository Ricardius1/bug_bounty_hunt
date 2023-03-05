import socketio
import asyncio
import requests


"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
"""Client side"""


"""======================================================================================================"""
"""Instantiating class objects and defining basic connection functions"""

sio = socketio.AsyncClient()
global userID
LATENCY = 0.5

# Function that creates connection between server and client
@sio.event
async def connect():
    print("Connected\n")


# Print out Connection Error if it occurred
@sio.event
async def connect_error():
    print("Connection Error")


# # Function that disconnects client from the server
@sio.event
async def disconnect():
    print("Disconnected")


"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


@sio.event
async def log_in():
    login = input("Login: ")
    password = input("Password: ")
    await sio.emit("login_check", {"login": login, "password": password}, callback=set_userID)
    await asyncio.sleep(LATENCY)
    if type(userID) is not int:
        print("User Not Found")
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
    while True:
        login = input("Login: ")
        password = input("Password: ")
        password_rep = input("Repeat Password: ")
        if password == password_rep:
            await sio.emit("register_user", {"login": login, "password": password})
            break
        else:
            print("Different passwords")


async def set_userID(user_num):
    global userID
    userID = user_num

async def display_results(data):
    print(data)


"""======================================================================================================"""
"""Client-side functions in the client-server communication"""


async def login_register():
    print("Options:\n1. Log-in\n2. Register")
    while True:
        try:
            option = int(input("Select option: "))
            if option == 1:
                await log_in()
                # If user is logged in start other functions
                if type(userID) is int:
                    break
            elif option == 2:
                await register()
                print("Options:\n1. Log-in\n2. Register")
        except ValueError:
            print("Please give a number")


@sio.event
async def program_interaction():
    print("\nUSER ACTIONS\n")
    count = 0
    while True:
        # Print these lines every 5 times
        if count % 5 == 0:
            print(" 1. New Scan\n 2. Check Your Scans\n 3. Get Scan Result \n 4. Exit")
        try:
            option = int(input("Select Option: "))
            if option == 2:
                await sio.emit("message_user_scans", {"userID": userID}, callback=display_results)
                await asyncio.sleep(LATENCY)
            elif option == 3:
                url = input("URL to check: ")
                await sio.emit("single_result", {"URL": url}, callback=display_results)
                await asyncio.sleep(LATENCY)
            elif option == 4:
                print("Program finish")
                await sio.disconnect()
                exit()
            elif option == 1:
                await start_inputs()
                await sio.wait()
            count += 1
        except ValueError:
            print("Please give a number")


# Asking user for inputs needed for program to start working
@sio.event
async def start_inputs():

    # Ask for program type
    print("\nChoose which type of program do you want to run: \n1: All URLs\n2: Single URL")
    while True:
        try:
            type_of_analysis = int(input("Choose(1-2): "))
            if type_of_analysis in range(1, 3):
                break
            else:
                print("Please give correct value")
        except ValueError:
            print("Please give a number")

    # Ask for start url
    url = ""
    while True:
        if type_of_analysis == 1:
            url = input("Give target url(https://example.com/): ")
        elif type_of_analysis == 2:
            url = input("Give target url(https://example.com/page?query): ")
            if "?" not in url:
                url = ""
        try:
            if 200 <= requests.get(url).status_code < 400:
                break
        except:
            print("Please give correct url")

    # Ask for level of complexity
    level_of_complexity = 0
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

    # Send data to the server with all inputs
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

    allowed_characters = "0123456789-,"
    while True:
        urls = input("Please select what URLs you want to check(press ENTER for all): ")
        no_spaces_urls = urls.replace(" ", "")
        if all(char in allowed_characters for char in no_spaces_urls):
            return no_spaces_urls.split(","), data["use_proxy"], data["sid"]
        print("Incorrect format")


# Print out the result of user's request
@sio.event
async def program_finish(data):
    scan_list = data["result"]
    print(scan_list)
    if scan_list is not []:
        for res in data["result"]:
            scan_res = res[0]
            payload_link = res[1]
            if res[0] == 5:
                print(f"Very high probability in {payload_link}")
            elif res[0] == 4:
                print(f"High probability in {payload_link}")
            elif res[0] == 3:
                print(f"Medium probability in {payload_link}")
            elif res[0] == 2:
                print(f"Low probability in {payload_link}")
    elif scan_list is []:
        print("SQL Injection wasn't found")
    await sio.emit("new_userscan", {})
    await program_interaction()



"""SECTION END"""
"""------------------------------------------------------------------------------------------------------"""


# Function that runs the client side functions
async def main():
    try:
        await sio.connect("http://localhost:8000", wait_timeout=4)
    except:
        print("Connection error, try again later")
        # TODO: use some method here to prevent from unresolved client session message
        exit()
    await login_register()
    await program_interaction()
    await sio.wait()


# Start client
if __name__ == "__main__":
    asyncio.run(main())
# TODO: find out why sometimes thee program automatically disconnects from the server.

"""========================================================================================================="""
"""========================================================================================================="""
"""========================================================================================================="""
