[**English**](./README.md)  | **中文**

# MCUProg

![github license](https://img.shields.io/github/license/Dozingfiretruck/MCUProg)[![Latest Release](https://img.shields.io/github/v/release/Dozingfiretruck/MCUProg?label=Release&logo=github)](https://github.com/Dozingfiretruck/nes/releases/latest)![windows](https://github.com/Dozingfiretruck/MCUProg/actions/workflows/windows.yml/badge.svg?branch=master)![linux](https://github.com/Dozingfiretruck/MCUProg/actions/workflows/linux.yml/badge.svg?branch=master)

github: [MCUProg](https://github.com/Dozingfiretruck/MCUProg) (推荐)

gitee: [MCUProg:](https://gitee.com/Dozingfiretruck/MCUProg) (由于同步问题可能导致更新不及时)

## 介绍

MCUProg是一款基于pyocd+PySide6的MUC烧录上位机软件(此软件只是用来学习pyocd和PySide6的练手项目,如果能帮到你那无比荣幸,你也可以任意修改)

**如果遇到使用问题请及时反馈**

## 软件架构

pyocd: 0.37.0
PySide6: 6.9.1

## 支持平台

- [x] Windows
- [x] Linux
- [ ] Macos

## 支持功能

- 支持Daplink V1、Daplink V2、stlink、Jlink烧录器
- 支持windows10以上系统，支持linux系统(ubuntu测试)
- 支持自定义本地pack文件以支持自定义芯片
- 支持读取芯片数据
- 支持读取烧录固件数据(目前支持bin、hex，elf、axf后续支持)
- 支持烧录时可选擦除芯片
- 支持bin固件自定义烧录地址

## LINUX使用说明

linux下要安装驱动, 驱动在仓库[udev](./udev/)目录下，使用说明参考[pyocd linux驱动安装](./udev/README.md)

并需要安装libusb : `apt install libusb-dev`

## 注意事项

如烧录失败请检查一下几点

1. 烧录器与芯片是否连接正常
2. 目标芯片是否选择正确
3. 芯片是否支持选择的烧录速度
4. 是否有中断下载比如拔出usb操作
5. 其他情况请尝试重启软件，如无法解决请及时反馈

## 下载地址

github: https://github.com/Dozingfiretruck/MCUProg/releases

gitee: https://gitee.com/Dozingfiretruck/MCUProg/releases

## 软件展示

![MCUProg](./doc/MCUProg.png)

