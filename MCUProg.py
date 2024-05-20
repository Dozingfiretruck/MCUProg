# Compilation mode, support OS-specific options
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --onefile
# nuitka-project-else:
#    nuitka-project: --standalone

# The PySide6 plugin covers qt-plugins
# nuitka-project: --enable-plugin=pyside6

# The following options are used to compile the program with Clang
# nuitka-project: --clang

# The output directory and other options
# nuitka-project: --output-dir=build
# nuitka-project: --disable-console
# nuitka-project: --include-data-dir=./icons=./icons
# nuitka-project: --include-data-dir=./resources=./resources
# nuitka-project-if: {OS} in ("Windows"):
#    nuitka-project: --windows-icon-from-ico=./icons/tool_icon.ico
# nuitka-project-if: {OS} in ("Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --linux-icon=./icons/tool_icon.ico



import sys,os,struct

from PySide6 import __version__ as PySide6_version
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,QThread,Signal,Slot)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication,QCheckBox,QFileDialog,QFontDialog,QMenu,
    QComboBox, QLabel, QLineEdit,QMainWindow, QProgressBar, QPushButton,QToolButton, 
    QSizePolicy,QStatusBar, QWidget,QDialog,QTextBrowser,QFrame,QGridLayout)

from pyocd.core.helpers import ConnectHelper
from pyocd.core.target import Target
from pyocd.core.memory_map import MemoryType
from pyocd.coresight.cortex_m import CortexM
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.tools.lists import ListGenerator
from pyocd._version import version as pyocd_version

from pyocd.target.pack.cmsis_pack import CmsisPack

version = "0.0.7"
author = "打盹的消防车"

if getattr(sys, 'frozen', False):
    run_dir = sys._MEIPASS
    exe_dir = os.path.dirname(os.path.realpath(sys.executable))
else:
    run_dir = os.path.dirname(os.path.abspath(__file__))
    exe_dir = run_dir

icon_path = os.path.join(run_dir,"icons","tool_icon.ico")
ui_font_path = os.path.join(run_dir,"resources","OPPOSans-regular.ttf")

mcuprog_tool_info = '''这是一个MCU烧录工具

版本: V{0}
作者: {1}

作者邮箱: dozingfiretruck@qq.com
作者仓库:
github: https://github.com/Dozingfiretruck
gitee: https://gitee.com/Dozingfiretruck

感谢:
PySide6: V{2}
pyocd: V{3}
UI字体: OPPOSans
'''.format(version,author,PySide6_version,pyocd_version)

class QComboBox2(QComboBox):
    pop_up = Signal()
    def showPopup(self):
        self.pop_up.emit()
        super(QComboBox2, self).showPopup()

class Thread2(QThread):
    finish = Signal(str)
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
    def run(self):
        res = self.func(*self.args)
        # 任务完成后发出信号
        self.finish.emit(res)

def programmer(MainWindow):
    board = MainWindow.session.board
    target = board.target

    if not MainWindow.file_path.endswith('.bin'):
        base_address = None
    else:
        if MainWindow.base_address_lineEdit.text() == '':
            base_address = None
        else:
            base_address = int(MainWindow.base_address_lineEdit.text(), base=0)

    if MainWindow.chip_erase_checkBox.isChecked():
        chip_erase = "chip"
    else:
        chip_erase = "auto"

    # Load firmware into device.
    FileProgrammer(MainWindow.session,
                    chip_erase=chip_erase,
                    smart_flash=False,
                    trust_crc=False,
                    keep_unwritten=True,
                    no_reset=True,
                    progress = MainWindow.progress
                    ).program(MainWindow.file_path,
                            base_address=base_address)
    # Reset
    target.reset_and_halt()
    
class MainWindow(QMainWindow):
    app_w = 960
    app_h = 480
    file_path = ''
    pack_path = ''
    allProbes = None
    Probe = None
    session = None
    frequency = {'10MHZ':10000000,'5MHZ':5000000,'2MHZ':2000000,'1MHZ':1000000,'500kHZ':500000,'200kHZ':200000,'100kHZ':100000,'50kHZ':50000,'20kHZ':20000,'10kHZ':10000,'5kHZ':5000}
    def __init__(self, parent = None) :
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MCUProg")

        self.setWindowTitle("MCUProg V"+version+" 作者:"+author)
        self.resize(self.app_w, self.app_h)
        self.setMinimumSize(QSize(self.app_w, self.app_h))
        self.setMaximumSize(QSize(self.app_w, self.app_h))
        # 图标
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        # 字体
        QFontDatabase.addApplicationFont(ui_font_path)
        ui_font = QFont("HarmonyOS Sans",10,QFont.Medium)
        self.setFont(ui_font)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName(u"centralwidget")
        
        # 菜单栏
        self.menubar = self.menuBar()
        self.menubar.setObjectName(u"menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName(u"statusbar")
        self.setStatusBar(self.statusbar)

        # 菜单栏 - 菜单
        self.menu_file = self.menubar.addMenu(QCoreApplication.translate("MCUProg", "菜单", None))
        # # 菜单 - 安装pack
        # self.install_pack = self.menu_file.addAction(QCoreApplication.translate("MCUProg", "安装pack", None))
        # self.install_pack.triggered.connect(self.click_install_pack)
        # 菜单 - 退出
        self.action_file_exit = self.menu_file.addAction(QCoreApplication.translate("MCUProg", "退出", None))
        self.action_file_exit.triggered.connect(self.click_exit)
        # 帮助
        self.menu_file = self.menubar.addMenu(QCoreApplication.translate("MCUProg", "帮助", None))
        # 帮助 -关于
        self.action_file_exit = self.menu_file.addAction(QCoreApplication.translate("MCUProg", "关于", None))
        self.action_file_exit.triggered.connect(self.click_about)

        self.mem_textBrowser = QTextBrowser(self.centralwidget)
        self.mem_textBrowser.setObjectName(u"mem_textBrowser")
        self.mem_textBrowser.setGeometry(QRect(10, 20, 480-20, 410))

        mem_menu = QMenu(self.centralwidget)
        self.mem_read_file = mem_menu.addAction(QCoreApplication.translate("MCUProg", "固件内存", None))
        self.mem_read_chip = mem_menu.addAction(QCoreApplication.translate("MCUProg", "芯片内存", None))
        self.mem_read_file.triggered.connect(lambda: self.mem_show("file"))
        self.mem_read_chip.triggered.connect(lambda: self.mem_show("chip"))

        self.mem_toolButton = QToolButton(self.centralwidget)
        self.mem_toolButton.setObjectName(u"mem_toolButton")
        self.mem_toolButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.mem_toolButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.mem_toolButton.setArrowType(Qt.ArrowType.DownArrow)
        self.mem_toolButton.setMenu(mem_menu)
        
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(480+10, 20, 460, 410))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayoutWidget = QWidget(self.frame)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 10, 440, 250))

        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        # self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # 第一行
        # pack标签
        self.pack_label = QLabel(self.gridLayoutWidget)
        self.pack_label.setObjectName(u"pack_label")
        # pack
        self.pack_lineEdit = QLineEdit(self.gridLayoutWidget)
        self.pack_lineEdit.setObjectName(u"pack_lineEdit")
        # pack选择
        self.pack_selection_button = QPushButton(self.gridLayoutWidget)
        self.pack_selection_button.setObjectName(u"pack_selection_button")

        self.gridLayout.addWidget(self.pack_label, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.pack_lineEdit, 0, 1, 1, 6)
        self.gridLayout.addWidget(self.pack_selection_button, 0, 7, 1, 1)

        # 第二行
        # 目标芯片标签
        self.target_label = QLabel(self.gridLayoutWidget)
        self.target_label.setObjectName(u"target_label")
        # 目标芯片选择
        self.targets_comboBox = QComboBox2(self.gridLayoutWidget)
        self.targets_comboBox.setObjectName(u"targets_comboBox")
        self.targets_comboBox.setEditable(True)
        self.targets_comboBox.setInsertPolicy(QComboBox.InsertAtBottom)
        self.targets_comboBox.setEditable(False)
        # 烧录速度标签
        self.speed_label = QLabel(self.gridLayoutWidget)
        self.speed_label.setObjectName(u"speed_label")
        # 烧录速度选择
        self.speed_comboBox = QComboBox(self.gridLayoutWidget)
        self.speed_comboBox.setObjectName(u"speed_comboBox")
        self.speed_comboBox.addItems(['10MHZ','5MHZ','2MHZ','1MHZ','500kHZ','200kHZ','100kHZ','50kHZ','20kHZ','10kHZ','5kHZ'])
        self.speed_comboBox.setEditable(True)
        self.speed_comboBox.setInsertPolicy(QComboBox.InsertAtBottom)
        self.speed_comboBox.setEditable(False)

        self.gridLayout.addWidget(self.target_label, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.targets_comboBox, 1, 1, 1, 5)
        self.gridLayout.addWidget(self.speed_label, 1, 6, 1, 1)
        self.gridLayout.addWidget(self.speed_comboBox, 1, 7, 1, 1)

        # 第三行
        # 烧录器标签
        self.downloard_label = QLabel(self.gridLayoutWidget)
        self.downloard_label.setObjectName(u"downloard_label")
        # 烧录器选择
        self.usb_comboBox = QComboBox2(self.gridLayoutWidget)
        self.usb_comboBox.setObjectName(u"usb_comboBox")
        self.usb_comboBox.setEditable(True)
        self.usb_comboBox.setInsertPolicy(QComboBox.InsertAtBottom)
        self.usb_comboBox.setEditable(False)
        # 连接按钮
        self.usb_connect_button = QPushButton(self.gridLayoutWidget)
        self.usb_connect_button.setObjectName(u"usb_connect_button")

        self.gridLayout.addWidget(self.downloard_label, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.usb_comboBox, 2, 1, 1, 6)
        self.gridLayout.addWidget(self.usb_connect_button, 2, 7, 1, 1)

        # 第四行
        # 烧录固件标签
        self.file_label = QLabel(self.gridLayoutWidget)
        self.file_label.setObjectName(u"file_label")
        # 烧录固件
        self.file_lineEdit = QLineEdit(self.gridLayoutWidget)
        self.file_lineEdit.setObjectName(u"file_lineEdit")
        # 烧录固件选择
        self.file_selection_button = QPushButton(self.gridLayoutWidget)
        self.file_selection_button.setObjectName(u"file_selection_button")

        self.gridLayout.addWidget(self.file_label, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.file_lineEdit, 3, 1, 1, 6)
        self.gridLayout.addWidget(self.file_selection_button, 3, 7, 1, 1)

        # 第五行
        # 烧录地址标签
        self.base_address_label = QLabel(self.gridLayoutWidget)
        self.base_address_label.setObjectName(u"base_address_label")
        # 烧录地址
        self.base_address_lineEdit = QLineEdit(self.gridLayoutWidget)
        self.base_address_lineEdit.setObjectName(u"base_address_lineEdit")
        # 是否擦除芯片
        self.chip_erase_checkBox = QCheckBox(self.gridLayoutWidget)
        self.chip_erase_checkBox.setObjectName(u"chip_erase_checkBox")

        self.gridLayout.addWidget(self.base_address_label, 4, 0, 1, 2)
        self.gridLayout.addWidget(self.base_address_lineEdit, 4, 2, 1, 5)
        self.gridLayout.addWidget(self.chip_erase_checkBox, 4, 7, 1, 1)

        # 第六行
        # 烧录进度条
        self.flash_progressBar = QProgressBar(self.gridLayoutWidget)
        self.flash_progressBar.setObjectName(u"flash_progressBar")
        self.flash_progressBar.setValue(0)
        # 烧录按钮
        self.flash_button = QPushButton(self.gridLayoutWidget)
        self.flash_button.setObjectName(u"flash_button")

        self.gridLayout.addWidget(self.mem_toolButton, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.flash_progressBar, 5, 1, 1, 6)
        self.gridLayout.addWidget(self.flash_button, 5, 7, 1, 1)
        
        # 信息显示
        self.gridLayoutWidget_info = QWidget(self.frame)
        self.gridLayoutWidget_info.setObjectName(u"gridLayoutWidget_info")
        self.gridLayoutWidget_info.setGeometry(QRect(10, 260, 440, 150))

        self.gridLayout_info = QGridLayout(self.gridLayoutWidget_info)
        self.gridLayout_info.setObjectName(u"gridLayout_info")
        # self.gridLayout_info.setContentsMargins(0, 0, 0, 0)
        
        # 第一行
        # 芯片信息
        self.chip_name_label = QLabel(self.gridLayoutWidget_info)
        self.chip_name_label.setObjectName(u"chip_name_label")
        self.chip_name = QLabel(self.gridLayoutWidget_info)
        self.chip_name.setObjectName(u"chip_name")

        self.gridLayout_info.addWidget(self.chip_name_label, 0, 0, 1, 1)
        self.gridLayout_info.addWidget(self.chip_name, 0, 1, 1, 6)
        
        # 第二行
        # 芯片RAM信息
        self.chip_ram_label = QLabel(self.gridLayoutWidget_info)
        self.chip_ram_label.setObjectName(u"chip_ram_label")
        self.chip_ram = QLabel(self.gridLayoutWidget_info)
        self.chip_ram.setObjectName(u"chip_ram")

        self.gridLayout_info.addWidget(self.chip_ram_label, 1, 0, 1, 1)
        self.gridLayout_info.addWidget(self.chip_ram, 1, 1, 1, 7)

        # 第三行
        # 芯片FLASH信息
        self.chip_flash_label = QLabel(self.gridLayoutWidget_info)
        self.chip_flash_label.setObjectName(u"chip_flash_label")
        self.chip_flash = QLabel(self.gridLayoutWidget_info)
        self.chip_flash.setObjectName(u"chip_flash")

        self.gridLayout_info.addWidget(self.chip_flash_label, 2, 0, 1, 1)
        self.gridLayout_info.addWidget(self.chip_flash, 2, 1, 1, 7)

        # 第四行
        # 芯片ROM信息
        self.chip_rom_label = QLabel(self.gridLayoutWidget_info)
        self.chip_rom_label.setObjectName(u"chip_rom_label")
        self.chip_rom = QLabel(self.gridLayoutWidget_info)
        self.chip_rom.setObjectName(u"chip_rom")

        self.gridLayout_info.addWidget(self.chip_rom_label, 3, 0, 1, 1)
        self.gridLayout_info.addWidget(self.chip_rom, 3, 1, 1, 7)

        # 第五行
        # 芯片OTHER信息
        self.chip_other_label = QLabel(self.gridLayoutWidget_info)
        self.chip_other_label.setObjectName(u"chip_other_label")
        self.chip_other = QLabel(self.gridLayoutWidget_info)
        self.chip_other.setObjectName(u"chip_other")

        self.gridLayout_info.addWidget(self.chip_other_label, 4, 0, 1, 1)
        self.gridLayout_info.addWidget(self.chip_other, 4, 1, 1, 7)

        # 第六行
        # 信息标签
        self.logs_label = QLabel(self.gridLayoutWidget_info)
        self.logs_label.setObjectName(u"logs_label")
        self.logs = QLabel(self.gridLayoutWidget_info)
        self.logs.setObjectName(u"logs")

        self.gridLayout_info.addWidget(self.logs_label, 5, 0, 1, 1)
        self.gridLayout_info.addWidget(self.logs, 5, 1, 1, 7)
        
        # 信号与槽
        self.pack_selection_button.clicked.connect(self.click_choose_pack)
        self.usb_comboBox.pop_up.connect(self.usb_selection)
        self.usb_connect_button.clicked.connect(self.usb_connect_button_click)
        self.targets_comboBox.pop_up.connect(self.target_selection)
        self.file_selection_button.clicked.connect(self.file_selection_button_click)
        self.flash_button.clicked.connect(self.flash_button_click)

        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()

        QMetaObject.connectSlotsByName(self)

        self.usb_selection()
        self.target_selection()
        self.mem_show()

    def retranslateUi(self):
        self.pack_label.setText(QCoreApplication.translate("MCUProg", u"pack文件", None))
        self.pack_selection_button.setText(QCoreApplication.translate("MCUProg", u"选择pack", None))

        self.file_selection_button.setText(QCoreApplication.translate("MCUProg", u"选择固件", None))
        self.flash_button.setText(QCoreApplication.translate("MCUProg", u"烧录", None))
        self.usb_connect_button.setText(QCoreApplication.translate("MCUProg", u"连接", None))
        self.target_label.setText(QCoreApplication.translate("MCUProg", u"目标芯片", None))
        self.downloard_label.setText(QCoreApplication.translate("MCUProg", u"烧录器", None))
        self.file_label.setText(QCoreApplication.translate("MCUProg", u"烧录固件", None))
        self.speed_label.setText(QCoreApplication.translate("MCUProg", u"烧录速度", None))
        self.base_address_label.setText(QCoreApplication.translate("MCUProg", u"烧录地址(.bin固件生效)", None))
        self.base_address_lineEdit.setText(QCoreApplication.translate("MCUProg", u"0x08000000", None))
        self.chip_erase_checkBox.setText(QCoreApplication.translate("MCUProg", u"擦除芯片", None))
        
        self.mem_toolButton.setText(QCoreApplication.translate("MCUProg", u"读取内存", None))
        self.chip_name_label.setText(QCoreApplication.translate("MCUProg", u"连接芯片:", None))
        self.chip_ram_label.setText(QCoreApplication.translate("MCUProg", u"RAM:", None))
        self.chip_flash_label.setText(QCoreApplication.translate("MCUProg", u"FLASH:", None))
        self.chip_rom_label.setText(QCoreApplication.translate("MCUProg", u"ROM:", None))
        self.chip_other_label.setText(QCoreApplication.translate("MCUProg", u"OTHER:", None))
        self.logs_label.setText(QCoreApplication.translate("MCUProg", u"日志:", None))
    
    def usb_selection(self):
        self.usb_probe()

    def target_selection(self):
        self.targets_comboBox.clear()
        list_targets = ListGenerator.list_targets()
        targets = list_targets['targets']
        for target in targets:
            # print(target['name'])
            self.targets_comboBox.addItem(target['name'])
        if self.pack_path != '':
            self.pack = CmsisPack(self.pack_path)
            for device in self.pack.devices:
                self.targets_comboBox.addItem(device.part_number.lower())

    def click_choose_pack(self):
        self.pack_path, _ = QFileDialog.getOpenFileName(self, "选择pack文件",self.pack_path or os.getcwd(),'(*.pack)')
        self.pack_lineEdit.setText(self.pack_path)

    def file_selection_button_click(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择烧录文件",self.file_path or os.getcwd(),'(*.bin *.hex *.elf *.axf)')
        self.file_lineEdit.setText(self.file_path)

    def usb_connect_button_click(self):
        # print("usb_connect_button_click")
        if self.usb_comboBox.currentText():
            if self.session and self.session.is_open:
                self.session.close()
                self.usb_connect_button.setText("连接")
                self.usb_comboBox.setEnabled(True)
                self.logs.setText("已断开连接")
            else:
                for Probe in self.allProbes:
                    if self.usb_comboBox.currentText() == Probe.description:
                        self.Probe = Probe
                        break
                # print(self.usb_comboBox.currentText())
                print(Probe,Probe.unique_id)
                # print(self.targets_comboBox.currentText())
                # print(self.frequency[self.speed_comboBox.currentText()])
                if self.Probe:
                    self.session = ConnectHelper.session_with_chosen_probe(
                                    blocking=False, 
                                    return_first=False, 
                                    pack=None if self.pack_path == '' else self.pack_path,
                                    unique_id=self.Probe.unique_id,
                                    frequency = self.frequency[self.speed_comboBox.currentText()],
                                    target_override = self.targets_comboBox.currentText())
                if self.session:
                    # print("project_dir: %s" % self.session.project_dir)
                    self.session.open()
                    # board = self.session.board
                    # print("Board MSG:")
                    # print("Board's name:%s" % board.name)
                    # print("Board's description:%s" % board.description)
                    # print("Board's target_type:%s" % board.target_type)
                    # print("Board's unique_id:%s" % board.unique_id)
                    # print("Board's test_binary:%s" % board.test_binary)
                    # print("Unique ID: %s" % board.unique_id)
                    # target = board.target
                    # print("Part number:%s" % target.part_number)
                    # memory_map = target.get_memory_map()
                    # ram_region = memory_map.get_default_region_of_type(MemoryType.RAM)
                    # rom_region = memory_map.get_boot_memory()
                    # print("menory map: ",memory_map)
                    # print("ram_region: ",ram_region)
                    # print("rom_region: ",rom_region)
                    self.usb_connect_button.setText("断开")
                    self.usb_comboBox.setEnabled(False)
                    self.logs.setText("已连接")
            self.chip_info_show()

    def progress(self, Value):
        self.flash_progressBar.setValue(Value*100)
        if Value == 1:
            self.logs.setText("烧录完成")
        else:
            self.logs.setText("烧录中...")

    def chip_info_show(self):
        if self.session and self.session.is_open:
            board = self.session.board
            target = board.target
            memory_map = target.get_memory_map()
            ram_region = memory_map.get_default_region_of_type(MemoryType.RAM)
            rom_region = memory_map.get_default_region_of_type(MemoryType.ROM)
            flash_region = memory_map.get_default_region_of_type(MemoryType.FLASH)
            other_region = memory_map.get_default_region_of_type(MemoryType.OTHER)
            # print("menory map: ",memory_map)
            # print("ram_region: ",ram_region)
            # print("ram_region.start: ",ram_region.start)
            # print("ram_region.end: ",ram_region.end)
            # print("ram_region.length: ",ram_region.length)
            # print("rom_region.access: ",rom_region.access)

            # print("rom_region: ",rom_region)
            # print("flash_region: ",flash_region)
            # print("other_region: ",other_region)

            # rom_region = memory_map.get_boot_memory()
            self.chip_name.setText(target.part_number)
            if ram_region:
                self.chip_ram.setText("start:0x%08X end:0x%08X length:0x%08X " % (ram_region.start, ram_region.end, ram_region.length))
            if flash_region:
                self.chip_flash.setText("start:0x%08X end:0x%08X length:0x%08X " % (flash_region.start, flash_region.end, flash_region.length))
            if rom_region:
                self.chip_rom.setText("start:0x%08X end:0x%08X length:0x%08X " % (rom_region.start, rom_region.end, rom_region.length))
            if other_region:
                self.chip_other.setText("start:0x%08X end:0x%08X length:0x%08X " % (other_region.start, other_region.end, other_region.length))
        else:
            self.chip_name.clear()
            self.chip_ram.clear()
            self.chip_flash.clear()
            self.chip_rom.clear()
            self.chip_other.clear()

    def mem_show(self, mem_type=None):
        self.mem_textBrowser.clear()
        self.mem_textBrowser.insertPlainText("   Address\t    0x00\t    0x04\t    0x08\t    0x0C\n")
        # self.file_path = "F:\\code\\codeup\\tiny_nfc\\build\\out\\tiny_nfc.elf"
        if mem_type == 'chip':
            if self.session and self.session.is_open:
                target = self.session.board.target
                boot_memory = target.get_memory_map().get_boot_memory()
                boot_memory_start = boot_memory.start
                boot_memory_end = boot_memory.end
                while boot_memory_start < boot_memory_end:
                    if boot_memory_start % 16 == 0:
                        self.mem_textBrowser.insertPlainText("0x%08X : " % boot_memory_start)
                    self.mem_textBrowser.insertPlainText("0x%08X" % target.read32(boot_memory_start))
                    boot_memory_start += 4
                    if boot_memory_start % 16 == 0:
                        self.mem_textBrowser.insertPlainText("\n")
                    else:
                        self.mem_textBrowser.insertPlainText("\t")

        elif mem_type == 'file'and self.file_path != '':
            if self.file_path.endswith('.bin'):
                with open(self.file_path, 'rb') as f:
                    # size = f.seek(0, os.SEEK_END)
                    # print(size)
                    # size = f.seek(0, 0)
                    base_address = 0
                    if self.base_address_lineEdit.text() == '':
                        if self.session:
                            base_address = self.session.board.target.get_memory_map().get_boot_memory().start
                    else:
                        base_address = int(self.base_address_lineEdit.text(), base=0)
                    while True:
                        data = f.read(16)
                        if len(data) != 16:
                            match len(data)/4:
                                case 1:
                                    num = struct.unpack('<I', data)
                                    self.mem_textBrowser.insertPlainText("0x%08X\t0x%08X\n" % (base_address,num[0]))
                                    break
                                case 2:
                                    num = struct.unpack('<II', data)
                                    self.mem_textBrowser.insertPlainText("0x%08X\t0x%08X\t0x%08X\n" % (base_address,num[0],num[1]))
                                    break
                                case 3:
                                    num = struct.unpack('<III', data)
                                    self.mem_textBrowser.insertPlainText("0x%08X\t0x%08X\t0x%08X\t0x%08X\n" % (base_address,num[0],num[1],num[2]))
                                    break
                                case _:
                                    break
                        num = struct.unpack('<IIII', data)
                        self.mem_textBrowser.insertPlainText("0x%08X\t0x%08X\t0x%08X\t0x%08X\t0x%08X\n" % (base_address,num[0],num[1],num[2],num[3]))
                        base_address += 16

            elif self.file_path.endswith(('.elf', '.axf')):
                with open(self.file_path, 'rb') as f:
                    if f.read(4) != b'\x7fELF':
                        return
                    if f.read(1) != b'\x01':
                        return
                    EI_DATA = f.read(1)
                    if EI_DATA == b'\x01':
                        print("Little Endian")
                    elif EI_DATA == b'\x02':
                        print("Big Endian")
                    else:
                        return
                    if f.read(1) != b'\x01':
                        return
                    EI_OSABI = f.read(1)
                    EI_ABIVERSION = f.read(1)
                    EI_PAD = f.read(7)
                    
                    if f.read(2) != b'\x02\x00':
                        return
                    e_machine = f.read(2)
                    if f.read(4) != b'\x01\x00\x00\x00':
                        return
                    e_entry = f.read(4)
                    a = struct.unpack('<I', e_entry)
                    print("Entry point: 0x%08X" % a[0])

                    e_phoff = f.read(4)
                    a = struct.unpack('<I', e_phoff) # 
                    print("e_phoff: 0x%08X" % a[0])
                    e_shoff = f.read(4)
                    a = struct.unpack('<I', e_shoff) # 
                    print("e_shoff: 0x%08X" % a[0])
                    e_flags = f.read(4)

                    e_ehsize = f.read(2)
                    a = struct.unpack('<H', e_ehsize)
                    print("e_ehsize: 0x%04X" % a[0])
                    e_phentsize = f.read(2)
                    a = struct.unpack('<H', e_phentsize)
                    print("e_phentsize: 0x%04X" % a[0])
                    e_phnum = f.read(2)
                    a = struct.unpack('<H', e_phnum)
                    print("e_phnum: 0x%04X" % a[0])
                    e_shentsize = f.read(2)
                    a = struct.unpack('<H', e_shentsize)
                    print("e_shentsize: 0x%04X" % a[0])
                    e_shnum = f.read(2)#7
                    e_shstrndx = f.read(2)#6

                    # print(e_entry,e_phoff,e_shoff,e_flags,e_ehsize,e_phentsize,e_phnum,e_shentsize,e_shnum,e_shstrndx)
                    
                    pass
            elif self.file_path.endswith('.hex'):
                with open(self.file_path, 'r') as f:
                    ULBA = 0
                    while True:
                        data = f.readline()
                        if data[0]!=':':
                            return
                        LOAD_RECLEN = int(data[1:3],16)
                        OFFSET = int(data[3:7],16)
                        RECTYP = int(data[7:9],16)
                        match RECTYP:
                            case 0:# 数据记录
                                base_address = ULBA<<16 | OFFSET
                                self.mem_textBrowser.insertPlainText("0x%08X" % (base_address))
                                for i in range(LOAD_RECLEN//4):
                                    self.mem_textBrowser.insertPlainText("\t0x%08X" % struct.unpack('<I', int(data[9+i*8:9+i*8+8],16).to_bytes(length=4, byteorder='big'))[0])
                                self.mem_textBrowser.insertPlainText("\n")
                            case 1:# 文件结束
                                return
                            case 2:# 扩展段地址-16位扩展段地址的段基址 SBA: 0:3 为0 4:19 USBA
                                USBA = int(data[9:9+LOAD_RECLEN*2],16)
                                # print(USBA)
                                pass
                            case 3:# 开始段地址-目标文件的执行起始地址-CS 和 IP 寄存器的 20 位段地址
                                CS_IP = int(data[9:9+LOAD_RECLEN*2],16)
                                # print(CS_IP)
                            case 4:# 扩展线性地址 扩展段线性地址的高16位,低16位在LOAD OFFSET中
                                ULBA = int(data[9:9+LOAD_RECLEN*2],16)
                                # print(ULBA)
                                # CHKSUM = data[13:17]
                                # print(CHKSUM)
                                pass
                            case 5:# 开始线性地址-目标文件的执行起始地址-EIP 寄存器的 32 位线性地址
                                EIP = int(data[9:9+LOAD_RECLEN*2],16)
                                # print(EIP)
                                pass
                            case _:
                                return
                        # 数据校验 CHKSUM 忽略

    def programmer_finished(self):
        print("programmer_finished")

    def flash_button_click(self):
        # print("flash_button_click")
        self.flash_progressBar.reset()
        self.flash_progressBar.setValue(0)
        if self.session and self.session.is_open and self.file_path!= '':
            self.thread_programmer = Thread2(programmer,self)
            self.thread_programmer.finish.connect(self.programmer_finished)
            self.thread_programmer.start()

    def usb_probe(self):
        self.allProbes = ConnectHelper.get_all_connected_probes(False, None, False)
        self.usb_comboBox.clear()
        if self.allProbes is None or len(self.allProbes) == 0:
            pass
            # print("No Probe",self.allProbes)
            return
        else:
            # print(self.allProbes)
            for Probe in self.allProbes:
                print(Probe)
                print(Probe.description)
                print(Probe.unique_id)
                self.usb_comboBox.addItem(Probe.description)

    def click_about(self):
        about_Dialog = QDialog(self)
        about_Dialog.resize(320, 320)
        about_Dialog.setMinimumSize(QSize(320, 320))
        about_Dialog.setMaximumSize(QSize(320, 320))
        about_Dialog.setWindowTitle("关于")
        icon = QIcon(icon_path)
        about_Dialog.setWindowIcon(icon)

        about_label = QLabel(about_Dialog)
        about_label.setObjectName(u"about_label")
        about_label.setGeometry(QRect(20, 20, 300, 300))

        about_label.setText(QCoreApplication.translate("MCUProg", mcuprog_tool_info, None))

        about_Dialog.exec()
    
    def click_exit(self):
        sys.exit(QApplication.instance().exec())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    win = MainWindow()
    win.show()
    app.exit(app.exec())



