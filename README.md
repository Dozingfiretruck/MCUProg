**English** | [中文](./README_zh.md) 

# MCUProg

![github license](https://img.shields.io/github/license/PeakRacing/MCUProg)[![Latest Release](https://img.shields.io/github/v/release/PeakRacing/MCUProg?label=Release&logo=github)](https://github.com/PeakRacing/nes/releases/latest)![windows](https://github.com/PeakRacing/MCUProg/actions/workflows/windows.yml/badge.svg?branch=master)![linux](https://github.com/PeakRacing/MCUProg/actions/workflows/linux.yml/badge.svg?branch=master)

github: [MCUProg](https://github.com/PeakRacing/MCUProg) (recommend)

gitee: [MCUProg:](https://gitee.com/PeakRacing/MCUProg) (updates may not be timely due to synchronization issues)

## Introduction

MCUProg is a MUC programming host computer software based on pyocd+PySide6 (this software is only used to learn pyocd and PySide6 practice projects, if it can help you, it is a great honor, you can also modify it at will)

**If you encounter any problems with use, please give feedback in time**

## Software Architecture

pyocd: 0.37.0
PySide6: 6.9.1

## Support platform 

- [x] Windows
- [x] Linux
- [ ] Macos

## Support features

- support daplinkv1、daplinkv2、stlink、jlink programmer 

- Support Windows 10 or above, support Linux system (Ubuntu test)

- Support custom local pack file to support custom chip

- Support reading chip data

- Support reading and burning firmware data (currently support bin, hex, ELF, AXF will be supported later)

- Support optional erasing chip during programming

- The bin firmware can be used to customize the programming address

## LINUX Instructions

Linux to install the driver,The driver is in the [udev](./udev/) directory of the repository,Instructions for [pyocd Linux driver installation](./udev/README.md)

and need install libusb : `apt install libusb-dev`

## Precautions

If the programming fails, please check the following points

1. Whether the connection between the programmer  and the chip is normal
2. Whether the target chip is selected correctly
3. Whether the chip supports the selected programming speed
4. Whether there is an interruption to the download, such as unplugging the USB operation
5. In other cases, please try to restart the software, if it cannot be solved, please give feedback in time

## Download link

github: https://github.com/PeakRacing/MCUProg/releases

gitee: https://gitee.com/PeakRacing/MCUProg/releases



## Software Presentation

![MCUProg](./doc/MCUProg.png)

## Discussion group

​	**Non-technical support, only for the purpose of interest exchange.**

![Communication](./docs/Communication.png)
