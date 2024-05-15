#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
import os

def open_file(path):
    """Open and return the file specified by path."""
    try:
        file = open(path, "r")
        return file
    except FileNotFoundError:
        print("Error! File not found.")
        sys.exit()


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    while True:
        char = get_next_character(input_file)
        if char == "" or not char.isspace():
            return char
    


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.

    rtype: list[int, str]
    """

    number = ""
    while True:
        char = get_next_character(input_file)
        if char == "":#end of file
            break
        elif char.isdigit():#append if digit
            number += char
        elif len(number) > 0:#break if not digit and number is not empty
            break
        
    #type cast number
    if len(number) == 0:
        number  = None
    else:
        number = int(number)

    return [number, char]
        

        



def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    while True: #find next alphabetical character
        char = get_next_character(input_file)
        if char == "":
            return 
        elif char.isalpha():
            name += char
        elif len(name) > 0:
            break
        

    

def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        path = os.getcwd() + "\\" + arguments[0] # is this what they want
        print("\nNow opening file : ", path)
        # Print the path provided and try to open the file for reading
        file_in = open_file(path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        while True:
            char = get_next_character(file_in)
            if char == "":
                break
            print(char, end="")

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        file_in = open_file(path)
        while True:
            char = get_next_non_whitespace_character(file_in)
            if char == "":
                break
            print(char, end="")

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file_in = open_file(path)
        while True:
            arr = get_next_number(file_in)
            number = arr[0]
            next_char = arr[1]
            if next_char == "":
                break
            print(number, ' ', end="")

        print("\nNow reading names...")
        # Print out all the names in the file

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        # name = MyNames()
        # bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
        #                 name.lookup("Ghastly"), name.lookup("Awful")]

if __name__ == "__main__":
    main()
