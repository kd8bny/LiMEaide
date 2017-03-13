# LiMEaide
## v1.2.0
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
limeaide.py [OPTIONS] REMOTE_IP
-h, --help
    show this dialog

-s, --sudoer
    Execute memory grab as sudoer. This is useful when root privileges are not granted

-o, --output
    Change name of output file. Default is dump.bin

-C, --dont-compress
    Do not compress memory file. By default memory is compressed on host. If you
    experience issues, toggle this flag. In my tests I see a ~60% reduction in file size

-V, --no-profile
    Do not create a volatility profile and do not include files for volatility.
    Volatility profile is generated on local machine

--force-clean
    If previous attempt failed then clean up client
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
If you want to build Volatility profiles you must use my forked version of LiME as this provides debugging symbols used by dwarfdump.
```
LiMEaide/tools/LiME
```
- How to...
```
cd tools
git clone https://github.com/kd8bny/LiME.git
```
#### darfdump
In order to build a volatility profile we need to be able to read the debugging symbols in the LKM. For this we need to install dwarfdump.
If you encounter any issues finding/installing dwarfdump see the volatility page [here](https://github.com/volatilityfoundation/volatility/wiki/Linux#creating-a-new-profile)
- DEB base
```
sudo apt-get install dwarfdump
```

- RPM base
```
sudo yum install libdwarf-tools
```

## Special Thanks and Notes
* The idea for this application was built upon the concept dreamed up by and the [Linux Memory Grabber](https://github.com/halpomeranz/lmg) project
* And of course none of this could be possible without the the amazing [LiME](https://github.com/504ensicsLabs/LiME) project
