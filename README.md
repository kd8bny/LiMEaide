# LiMEaide
## v2.0.0
## by Daryl Bennett - kd8bny[at]gmail[dot]com

## About
LiMEaide is a python application designed to remotely or locally dump RAM of a Linux client and create a volatility profile for later analysis on your local host. I hope that this will simplify Linux digital forensics in a remote environment. In order to use LiMEaide all you need to do is feed a remote Linux client IP address, sit back, and consume your favorite caffeinated beverage.

LiMEaide has 3 primary modes of operation

1. Remote - Initiates connection with SSH and transfers data over SFTP
2. Socket - Initiates a connection with SSH but transfers the memory image over a TCP socket. This means that the image is NOT written to disk. Tools are still transfered over SFTP.
3. Locally - Have a copy of LiMEiade on a flash drive or other device. Does not transfer any data to the client, maintain execution in its working directory. All transfers are completed with internal methods and no network sockets are opened.

## Wiki
For more detailed usage checkout the [wiki](https://github.com/kd8bny/LiMEaide/wiki)

## How To
### TL;DR
#### Remote
```
python3 limeaide.py <IP>
```
and magic happens.
#### Local
```
python3 limeaide.py local
```
and local magic happens.

Local transfer requires the machine to have python 3 installed and dependencies. I recommend using python3-virtualenv to provide dependencies without installing on the system.

### Detailed usage
```
limeaide.py [OPTIONS] REMOTE_IP
-h, --help
    Shows the help dialog

-u, --user : <user>
    Execute memory grab as sudo user. This is useful when root privileges are not granted.

-k, --key : <path to key> 
    Use a SSH Key to connect

-s, --socket : <port> 
    Use a TCP socket instead of a SFTP session to transfer data. Does not write the memory image to disk, but will transfer other needed files.

-o, --output : <Name desired for output> 
    Name the output file

-f, --format : <Format for LiME>
    Change the output format. Valid options are raw|lime|padded

-d, --digest : <digest>
    Use a different digest algorithm. See LiME docs for valid options
    Use 'None' to disable. 

-C, --compress
    Compress transfer over the wire. This will not work with socket or local transfers.

-p, --profile : <distro> <kernel version> <arch>
    Skip the profiler by providing the distribution, kernel version, and architecture of the remote client.

-N, --no-profiler
    Do NOT run profiler and force the creation of a new module/profile for the client.

-c, --case : <case num>
    Append case number to front of output directory.

-v, --verbose
    Display verbose output

--force-clean
    If previous attempt failed then clean up client
```

- For more detailed usage checkout the [wiki](https://github.com/kd8bny/LiMEaide/wiki)
- For editing the configuration file see [here](https://github.com/kd8bny/LiMEaide/wiki/The-Config-File)
- To import modules or external modules, just copy the module `*.ko` into the profiles directory. After you copy run LiMEaide and the profiler will recognize the new profile.

```
./profiles/
```

## Set-up
### Dependencies
#### python
- DEB base
```
sudo apt-get install python3-paramiko python3-termcolor
```
- RPM base
```
sudo yum install python3-paramiko python3-termcolor
```
- pip3
```
sudo pip3 install paramiko termcolor
```

#### Installing dwarfdump
In order to build a volatility profile we need to be able to read the debugging symbols in the LKM. For this we need to install dwarfdump.
If you encounter any issues finding/installing dwarfdump see the volatility page [here](https://github.com/volatilityfoundation/volatility/wiki/Linux#creating-a-new-profile)
- DEB package manager
```
sudo apt-get install dwarfdump
```

- RPM package manager
```
sudo yum install libdwarf-tools
```

#### LiME
##### Auto-Install
By default LiMEaide will automatically download and place LiME in the correct directory. However, if you are disconnected from a network proceed with manual installation method in the section below.
##### Manually install LiME
In order to use LiME you must download and move the source into the **LiMEaide/tools** directory. Make sure the the LiME folder is named **LiME**. The full path should be as follows:
```
LiMEaide/tools/LiME/
```
How to...

 1. Download [LiME v1.8.1](https://github.com/504ensicsLabs/LiME/archive/v1.8.1.zip)
 2. Extract into `LiMEaide/tools/`
 3. Rename folder to `LiME`

## Limits at this time
- Only supports bash. Use other shells at your own risk
- Modules must be built on remote client. Therefore remote client must have proper headers installed.
  - Unless you follow [this](https://github.com/kd8bny/LiMEaide/wiki/Building-Out-of-Tree-Modules) guide for compiling external kernel modules. Once compiled, copy module **.ko** to LiMEaide profiles directory.

## Special Thanks and Notes
* The idea for this application was built upon the concept dreamed up by and the [Linux Memory Grabber](https://github.com/halpomeranz/lmg) project
* And of course none of this could be possible without the amazing [LiME](https://github.com/504ensicsLabs/LiME) project
