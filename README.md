# Check For Down Nodes in SLURM

## What this code does
It uses SLURM's `sinfo` to monitor the nodes that get set to the 'down' state.
Nodes can get set to 'down' for a variety of reasons:
1. Admin's uses `scontrol` to set to down
2. If they fall off the network
3. If they reboot and slurmd isn't restarted

On our system, I run this hourly as a cron job as a basic check that notifies me (by email) when a node goes down or comes back up.
This code uses a file (in the code directory) called `down_nodes.txt` which is a list of nodes that are down.
Emails are _only_ sent when a _new_ node either comes up (no longer in 'down' state) or _new_ node goes down.

## Installation
Simply copy the directory where you want it to live.

### Dependencies
You will need:
1. Python 3
2. Linux operating system 
3. GNU core-utils, including `sort` and `uniq`
4. SLURM

### Tested On
1. Python 3.6.5
2. CentOS 6.10
3. coreutils 8.4
4. SLURM 17.11.7

## Running
### Production mode
Uses sinfo to see what nodes are 'down' and compare to nodes previously in `down_nodes.txt`. 
Email only sent if there is a difference between `sinfo`'s report of down nodes and 'down_nodes.txt'
Nodes can change state and be up (i.e. node no longer in `down_nodes.txt`) or nodes can be 'down' (i.e. sinfo reports as down and node is not in `down_nodes.txt`).

To Run : 
`python check_for_down_nodes.py your.email@address.com`

### Test mode
Runs a few simple tests (you'll have to check by hand) that verifies the code is working reasonably.  

To Run : 
`python check_for_down_nodes.py your.email@address.com test`
