from sys import platform
from os import system

"""
Code used for user interface
"""


def chooseMenu(options: list, indexed: bool = True, hideIndex: list = [], horizontal: bool = False, headers: dict = {}):
    """
        @brief <- Prints options, and has menu to choose which one

        @params:
            @options <- Series found from previous search
            @indexed <- If true, when options are printed show the index on the left
            @hideIndex <- list containing indexes to not be printed
                          Ex: If i didnt want the link to be shown in the list, i would pass hideIndex = [1] where 1 is the index that i dont want printed
                          options=["sherlock","http://link.com"]
            @horizontal <- Prints items in horizontal order instead of vertival

        @returns <- Chosen Series array
    """

    # Choosing options menu
    while(True):
        execute_OS_command("clear", "cls")
        # Showing headers if any exist
        for headerTitle, headerValue in headers.items():
            print(f"{headerTitle}: {headerValue} ")
        # Showing search results if any found
        for idx, item in enumerate(options):

            if indexed:
                print(f"[{str(idx+1)}] ", end="")

            for itemIndex, value in enumerate(item):
                # Show every option except ones whose index is inside hideIndex
                if itemIndex not in hideIndex:
                    print(value, end=" ")
                # Dont show links to user
                # if "http" not in value:
                    #print(value, end=" ")

            print("\n" if not horizontal else "\t", end="")

        if horizontal:
            print("\n")

        # Return chosen option from options list, with correct user input validation
        return options[getOptionNumber(options)]


def getOptionNumber(option_list: list):
    """
        Correctly validates user input when choosing and id from list

        @returns index of chosen option
    """

    while(True):
        try:
            option = int(input("Número: ")) - 1
            if(option < 0 or option > len(option_list) - 1):
                print("Tens de escolher um número dentro do escopo mostrado.")
            else:
                return option
        except Exception:
            print("Tens de escolher um número.")


def playVLCStream(stream_url: str):
    vlc_instance = vlc.Instance()

    # creating a media player
    player = vlc_instance.media_player_new(stream_url)

    # play the video
    player.play()

    print("Find way to detect if player is dead")
    print(dir(player))


def execute_OS_command(linux_command: str, windows_command: str, args: list = []):
    """
        @brief Executes a command based on OS

        @linux_command <- if OS is linux, executes linux_command
        @windows_command <- if OS is windows, executes windows_command
        @*args <- arguments for the command, ex: "ls -la /usr/bin/" where ls is the linux command, and *args was ["-la", "/usr/bin/"]
    """

    exe_command = ""

    if platform in ["linux", "linux2", "darwin"]:
        exe_command = linux_command
    elif platform == "win32":
        exe_command = windows_command

    # If there are args, they will be added, if not, args will become empty string
    args = " ".join(args)

    exe_command = exe_command + " " + args
    print("Executing VLC")

    system(exe_command)
