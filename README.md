# LiMEaide
## v1.3.0

## About
LiMEaide is a python application designed to remotely dump RAM of a Linux client and create a volatility profile for later analysis on your local host. I hope that this will simplify Linux digital forensics in a remote environment. In order to use LiMEaide all you need to do is feed a remote Linux client IP address, sit back, and consume your favorite caffeinated beverage.

## How To
### TL;DR
```
python3 limeaide.py <IP>
```
and magic happens.

For more detailed usage checkout the [wiki](https://github.com/kd8bny/LiMEaide/wiki)
For editing the configuration file see [here]()

### Detailed usage
```
limeaide.py [OPTIONS] REMOTE_IP
-h, --help
    Shows the help dialog

-u, --user : <user>
    Execute memory grab as sudo user. This is useful when root privileges are not granted.

-p, --profile : <distro> <kernel version> <arch>
    Skip the profiler by providing the distribution, kernel version, and architecture of the remote client.

-N, --no-profiler
    Do NOT run profiler and force the creation of a new module/profile for the client.

-C, --dont-compress
    Do not compress memory file. By default memory is compressed on host. If you experience issues, toggle this flag. In my tests I see a ~60% reduction in file size

--delay-pickup
    Execute a job to create a RAM dump on target system that you will retrieve later.  The stored job
    is located in the scheduled_jobs/ dir that ends in .dat

-P, --pickup <path to job file .dat>
    Pick up a job you previously ran with the --delayed-pickup switch.
    The file that follows this switch is located in the scheduled_jobs/ directory
    and ends in .dat

-o, --output : <name>
    Change name of output file. Default is dump.bin

-c, --case : <case num>
    Append case number to front of output directory.

--force-clean
    If previous attempt failed then clean up client
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
#### LiME
In order to use LiME you must download and move the source into the **LiMEaide/tools** directory. Make sure the the LiME folder is named **LiME**. The full path should be as follows:
NOTE: If you would like to build Volatility profiles, you must use my forked version of LiME. This provides debugging symbols used by dwarfdump.
```
LiMEaide/tools/LiME/
```
How to...

 1. Download [LiME v1.7.8.1](https://github.com/kd8bny/LiME/archive/v1.7.8.1.zip)
 2. Extract into `LiMEaide/tools/`
 3. Rename folder to `LiME`

#### dwarfdump
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

## Special Thanks and Notes
* The idea for this application was built upon the concept dreamed up by and the [Linux Memory Grabber](https://github.com/halpomeranz/lmg) project
* And of course none of this could be possible without the amazing [LiME](https://github.com/504ensicsLabs/LiME) project

## Limits at this time
- Support on for bash. Use other shells at your own risk
- Modules must be built on remote client. Therefore remote client must have proper headers installed.
