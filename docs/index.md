---
layout: default
title: LiMEaide
---

# LiMEaide
## v2.0.0
## About
LiMEaide is a python application designed to remotely or locally dump RAM of a Linux client and create a volatility profile for later analysis on your local host. I hope that this will simplify Linux digital forensics in a remote environment. In order to use LiMEaide all you need to do is feed a remote Linux client IP address, sit back, and consume your favorite caffeinated beverage.

LiMEaide has 3 primary modes of operation

1. Remote - Initiates connection with SSH and transfers data over SFTP
2. Socket - Initiates a connection with SSH but transfers the memory image over a TCP socket. This means that the image is NOT written to disk. Tools are still transfered over SFTP.
3. Locally - Have a copy of LiMEiade on a flash drive or other device. Does not transfer any data to the client, maintain execution in its working directory. All transfers are completed with internal methods and no network sockets are opened.

For more detailed usage checkout the [wiki](https://github.com/kd8bny/LiMEaide/wiki)

## Download Now
[Github](https://github.com/kd8bny/LiMEaide/releases)

![LiMEaide Demo](assets/images/LiMEaide2.gif)
v1.2.3