# Author  : Ali Snedden
# Date    : 4/5/18
# Purpose : Create chron job to monitor cluster node status so i don't have
#           to think about it
# Debug  : Did some cursory tests. Should work..
#
# License : MIT
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.


import os
import re
import sys
import time

def exit_with_error(string):
    """
    ARGS:
        string      : str to print then exit
    DESCRIPTION:
        Print string. Exit with value 1
    RETURN:
    DEBUG:
        1. Tested, it worked
    FUTURE:
    """
    sys.stderr.write(string)
    sys.exit(1)


def print_help(Arg):
    """
    ARGS:
        arg     : exit value
    RETURN:
        N/A
    DESCRIPTION:
        Print Help. Exit with value arg
    DEBUG:
        1. Tested, it worked
    FUTURE:
    """
    sys.stdout.write(
            "\nUSAGE : check_for_down_nodes.py emailAddress [test]\n\n"
            "    emailAddress : your email address here \n"
            "    [test] : if present use test strings\n"
            "             if absent use sinfo\n\n")
    sys.exit(Arg)


def email_down_nodes(EmailAddress = None, StringL = None):
    """
    ARGS:
        StringL : string list from which to get down nodes
    RETURN:
    DESCRIPTION:
    DEBUG:
    FUTURE:
    """
    curDownL=[]
    alreadyDown=[]
    newDown=[]
    newUp=[]
    prefix=None
    overwrite=False
    codePath=os.path.dirname(os.path.realpath(__file__))
    
    curDownL = StringL.split()
    
    # Get already down nodes
    fdown = open("{}/down_nodes.txt".format(codePath), "r")
    for line in fdown:
        alreadyDown.append(line.strip())
    fdown.close()
    
    # Find new down nodes
    for node in curDownL:
        if(node not in alreadyDown):
            newDown.append(node)
            overwrite=True
    
    # See if any nodes back in service
    for node in alreadyDown:
        if(node not in curDownL):
            newUp.append(node)
            overwrite=True
    
    # Overwrite down_nodes.txt b/c new nodes found
    if(overwrite == True):
        fdown = open("{}/down_nodes.txt".format(codePath),"w+")
        for node in curDownL:
            fdown.write("{}\n".format(node))
        fdown.close()
        # Write email...
        email=open("{}/email.txt".format(codePath),"w+")
        email.write("New nodes DOWN:\n")
        for node in newDown:
            email.write("\t{}\n".format(node))
        
        email.write("New nodes UP:\n")
        for node in newUp:
            email.write("\t{}\n".format(node))
        email.close()
        os.system("mail -s Baker_Update {} < {}/email.txt".format(EmailAddress, codePath))
    else:
        email=open("{}/email.txt".format(codePath),"w+")
        email.close()



def main():
    """
    ARGS:
    RETURN:
    DESCRIPTION:
    DEBUG:
    FUTURE:
    """
    if(sys.version_info[0] != 3):
        exit_with_error("ERROR!!! Runs with python3, NOT python-{}\n\n".format(
                    sys.version_info[0]))
    nArg = len(sys.argv)
    if(nArg == 2 and (sys.argv[1][0:3] == "--h" or sys.argv[1][0:2] == "-h")):
        print_help(0)
    ## 2 args - use test strings
    elif(nArg == 3):
        if(sys.argv[2] == 'test'):
            useTestStr = True
        else:
            print_help(1)
    ## 1 args - use sinfo
    elif(nArg == 2):
        useTestStr = False
    ## Some error
    elif(nArg != 2 and nArg != 3):
        print_help(1)

    if('@' not in sys.argv[1]):
        exit_with_error("ERROR!!! {} is _not_ an email address\n".format(sys.argv[1]))
    else:
        emailAddress = sys.argv[1]
    codePath=os.path.dirname(os.path.realpath(__file__))

    if(useTestStr == True):
        # Clobber down_nodes.txt for testing
        fdown = open("{}/down_nodes.txt".format(codePath), "w+")
        fdown.close()
        stringL = 'gpu04\nnode15\n'
        email_down_nodes(EmailAddress=emailAddress, StringL = stringL)
        print("NEW : \n\tDOWN = gpu04, node15\n\tUP   = ")
        time.sleep(5)

        stringL = 'gpu04\nnode16\n'
        email_down_nodes(EmailAddress=emailAddress, StringL = stringL)
        print("NEW : \n\tDOWN = node16 \n\tUP   = node15")
        time.sleep(5)

        stringL = 'gpu04\ngpu05\n'
        email_down_nodes(EmailAddress=emailAddress, StringL = stringL)
        print("NEW : \n\tDOWN = gpu05\n\tUP   = node16")
        time.sleep(5)

        stringL = ''
        email_down_nodes(EmailAddress=emailAddress, StringL = stringL)
        print("NEW : \n\tDOWN = \n\tUP   = gpu04, gpu05")
        time.sleep(5)

    if(useTestStr == False):
        # Print each node b/c it is a PITA to parse the default format.
        stringL = os.popen("sinfo -o '%all' | grep down | awk 'BEGIN{FS=\"|\"}{print $11}' | sort | uniq").read()
        email_down_nodes(EmailAddress=emailAddress, StringL = stringL)
    

    sys.exit(0)


if __name__ == "__main__":
    main() 


