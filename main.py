import os

# hardcoded "secret" (security issue)
API_KEY = "1234567890-secret-key"

def divide(a, b):
    return a / b   # no error handling (division by zero risk)

def get_user_input():
    return input("Enter number: ")

def process():
    x = get_user_input()
    y = get_user_input()

    # no validation (string to int crash risk)
    result = divide(int(x), int(y))

    print("Result is " + result)  # type error (int + str)

process()