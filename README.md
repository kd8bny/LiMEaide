# LiMEaide
## v1.0.1
## About
LiMEaide is a python wrapper that will simplify Linux digital forensics in an enterprise environment. All you need to do is feed LiMEaide a remote Linux client IP, sit back, and consume your favorite caffeinated beverage.

## How To
### TL;DR
```
python3 limeaide.py <IP>
```
and magic happens

### Detailed usage
```
limeaide.py [-h] [-o <outputfile>] [-s <sudoer>] [--force-clean] <remote host IP>
-h show this dialog
-s Execute memory grab as sudoer. This is useful when root privileges are not granted
-o Declare name of output file. Default is dump.bin
--force-clean If previous attempt failed then clean up client
```

## Set-up
### Dependencies
#### python3-paramiko
- DEB base
```
sudo apt-get install python3-paramiko
```

- RPM base
```
sudo yum install python3-paramiko
```
#### LiME
In order to use LiME you must download and mv the source into the **LiMEaide/tools** directory. Make sure the the LiME folder is named **LiME**. The full path shold be as follows:
```
LiMEaide/tools/LiME
```

## Special Thanks and Notes
* The idea for this application was built upon the concept dreamed up by and the [Linux Memory Grabber](https://github.com/halpomeranz/lmg) project
* And of course none of this could be possible without the the amazing [LiME](https://github.com/504ensicsLabs/LiME) project

## TODO
Add support to create volatility profile
