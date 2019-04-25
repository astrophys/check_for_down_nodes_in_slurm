#!/bin/env python
# Author : Ali Snedden
# Date : 4/5/18
# Purpose : Create chron job to monitor cluster node status so i don't have
#           to think about it
# Debug  : Did some cursory tests. Should work..
#
import os
import re
import sys

stringL = os.popen("sinfo | grep down | grep -v kapoor | awk '{print $6}' ").read()
stringL = stringL.split()

curDown=[]
alreadyDown=[]
newDown=[]
newUp=[]
prefix=None
overwrite=False

for string in stringL:
    tokL = string.split(",")
    if(len(tokL) > 1):
        for tok in tokL:
            if("gpu" in tok):
                curDown.append(tok)
            # Complex parsing of output from slurm.. PITA
            if("[" in tok):
                prefix = tok.split("[")[0]
                if("-" in tok.split("[")[1]):
                    minNum = int(tok.split("[")[1].split("-")[0])
                    maxNum = int(tok.split("[")[1].split("-")[1])
                    for i in range(minNum, maxNum + 1):
                        curDown.append("{}{}".format(prefix,i))
                else:
                    num = int(tok.split("[")[1])
                    curDown.append("{}{}".format(prefix,num))
                        
            elif("]" in tok and "[" not in tok):
                if("-" in tok.split("]")[1]):
                    # assume prefix already set
                    if(prefix != None):
                        minNum = int(tok.split("]")[0].split("-")[0])
                        maxNum = int(tok.split("]")[0].split("-")[1])
                        for i in range(minNum, maxNum + 1):
                            curDown.append("{}{}".format(prefix,i))
                    else:
                        sys.stderr.write("ERROR!! prefix NOT set. {}".format(tokL))
                        sys.exit(1)
                else:
                    num = int(tok.split("]")[0])
                    curDown.append("{}{}".format(prefix,num))
            # Middle nodes..
            else:
                if("-" in tok):
                    minNum = int(tok.split("-")[0])
                    maxNum = int(tok.split("-")[1])
                    for i in range(minNum, maxNum + 1):
                        curDown.append("{}{}".format(prefix,i))
                else:
                    num = int(tok)
                    curDown.append("{}{}".format(prefix,num))
                
                    

    else:
        curDown.append(tokL[0])

curDown = set(curDown)      # Remove duplicates due to Kapoor's list and still get his nodes

#print(curDown)

# Get already down nodes
fdown = open("/gpfs0/home/group/user/Code/Python/check_for_down_nodes/down_nodes.txt", "r")
for line in fdown:
    alreadyDown.append(line.strip())
fdown.close()

# Find new down nodes
for node in curDown:
    if(node not in alreadyDown):
        newDown.append(node)
        overwrite=True

# See if any nodes back in service
for node in alreadyDown:
    if(node not in curDown):
        newUp.append(node)
        overwrite=True



# Overwrite down_nodes.txt b/c new nodes found
if(overwrite == True):
    fdown = open("/gpfs0/home/group/user/Code/Python/check_for_down_nodes/down_nodes.txt","w+")
    for node in curDown:
        fdown.write("{}\n".format(node))
    fdown.close()
    # Write email...
    email=open("/gpfs0/home/group/user/Code/Python/check_for_down_nodes/email.txt","w+")
    email.write("New nodes DOWN:\n")
    for node in newDown:
        email.write("\t{}\n".format(node))
    
    email.write("New nodes UP:\n")
    for node in newUp:
        email.write("\t{}\n".format(node))
    email.close()
    os.system("mail -s Baker_Update first.last@gmail.com < /gpfs0/home/group/user/Code/Python/check_for_down_nodes/email.txt")
else:
    email=open("/gpfs0/home/group/user/Code/Python/check_for_down_nodes/email.txt","w+")
    email.close()



sys.exit(0)
