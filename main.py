import os, sys

x=10
y =20

def addNumbers(a,b):
    result=a+b
    unused_var = 99
    return result


def print_message():
    msg="Hello World"
    print(   msg  )


def long_function():
    very_long_variable_name = "this is a very long line that will definitely exceed the standard pep8 line length limit if flake8 is strict enough"
    return very_long_variable_name


class testclass:
    def __init__(self,value):
        self.value=value

    def showValue(self):
        print(self.value)



addNumbers(5,6)
print_message()
obj=testclass(100)
obj.showValue()