# LiMEaide
## v1.0.0
## About
LiMEaide is a python wrapper that will simplify Linux digital forensics in an enterprise environment. All you need to do is feed LiMEaide a remote Linux client IP, sit back, and consume your favorite caffeinated beverage.

## Table of Contents
* [Dependancies]()


## How To
### BLUF - bottom line up front
```
python limeaide.py <IP>
```
and thats it... :)

## Deatiled ussage
```
limeaide.py [-h] [-o <outputfile>] [-s <sudoer>] <remote host IP>
-h show this dialog
-s Execute memory grab as sudoer. This is useful when root privileges are not granted
-o Declare name of output file. Default is dump.bin
```

# Dependancies
python-paramiko

# Special Thanks and Notes
* The idea for this application was built upon the concept dreamed up by and the [Linux Memory Grabber](https://github.com/halpomeranz/lmg) project
* And of course none of this could be possible without the the amazing [LiME](https://github.com/504ensicsLabs/LiME) project

#TODO
Add support to create volitility profile
