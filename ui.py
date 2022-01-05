"""
Code used for user interface
"""


def chooseMenu(options: list, indexed: bool = True):
    """
        @brief <- Prints options, and has menu to choose which one

        @params:
            @options <- Series found from previous search
            @indexed <- If true, when options are printed show the index on the left

        @returns <- Chosen Series array
    """
    # Choosing options menu
    while(True):
        # Showing search results if any found
        for idx, item in enumerate(options):

            if indexed:
                print(f"[{str(idx+1)}] ", end="")

            for value in item:
                # Dont show links to user
                if "http" not in value:
                    print(value, end=" ")

            print("\n", end="")

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
