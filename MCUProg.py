import sys,os

from PySide6 import __version__ as PySide6_version
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,QThread,Signal,Slot)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication,QCheckBox,QFileDialog,QFontDialog,
    QComboBox, QLabel, QLineEdit,QMainWindow, QProgressBar, QPushButton, 
    QSizePolicy,QStatusBar, QWidget,QDialog)

from pyocd.core.helpers import ConnectHelper
from pyocd.core.target import Target
from pyocd.core.memory_map import MemoryType
from pyocd.coresight.cortex_m import CortexM
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.tools.lists import ListGenerator
from pyocd._version import version as pyocd_version

version = "0.0.3"

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
作者: 打盹的消防车
作者仓库: 
https://github.com/Dozingfiretruck
https://gitee.com/Dozingfiretruck

感谢:
PySide6: V{1}
pyocd: V{2}
UI字体: OPPOSans
'''.format(version,PySide6_version,pyocd_version)

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
    app_w = 480
    app_h = 280
    file_path = ''
    allProbes = None
    Probe = None
    session = None
    frequency = {'10MHZ':10000000,'5MHZ':5000000,'2MHZ':2000000,'1MHZ':1000000,'500kHZ':500000,'200kHZ':200000,'100kHZ':100000,'50kHZ':50000,'20kHZ':20000,'10kHZ':10000,'5kHZ':5000}
    def __init__(self, parent = None) :
        super().__init__(parent)
        if not self.objectName():
            self.setObjectName(u"MCUProg")
        self.setWindowTitle("MCUProg V"+version)
        self.resize(self.app_w, self.app_h)
        self.setMinimumSize(QSize(self.app_w, self.app_h))
        self.setMaximumSize(QSize(self.app_w, self.app_h))
        # 图标
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        # 字体
        QFontDatabase.addApplicationFont(ui_font_path)
        # QFontDatabase.applicationFontFamilies(id)
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

        # 目标芯片标签
        self.target_label = QLabel(self.centralwidget)
        self.target_label.setObjectName(u"target_label")
        self.target_label.setGeometry(QRect(20, 20, 50, 20))
        # 目标芯片选择
        self.targets_comboBox = QComboBox2(self.centralwidget)
        self.targets_comboBox.setObjectName(u"targets_comboBox")
        self.targets_comboBox.setGeometry(QRect(80, 20, 160, 20))
        # 烧录速度标签
        self.speed_label = QLabel(self.centralwidget)
        self.speed_label.setObjectName(u"speed_label")
        self.speed_label.setGeometry(QRect(260, 20, 50, 20))
        # 烧录速度选择
        self.speed_comboBox = QComboBox(self.centralwidget)
        self.speed_comboBox.setObjectName(u"speed_comboBox")
        self.speed_comboBox.setGeometry(QRect(320, 20, 120, 20))
        self.speed_comboBox.addItems(['10MHZ','5MHZ','2MHZ','1MHZ','500kHZ','200kHZ','100kHZ','50kHZ','20kHZ','10kHZ','5kHZ'])
        # 烧录器标签
        self.downloard_label = QLabel(self.centralwidget)
        self.downloard_label.setObjectName(u"downloard_label")
        self.downloard_label.setGeometry(QRect(20, 60, 53, 20))
        # 烧录器选择
        self.usb_comboBox = QComboBox2(self.centralwidget)
        self.usb_comboBox.setObjectName(u"usb_comboBox")
        self.usb_comboBox.setGeometry(QRect(80, 60, 260, 23))
        # 连接按钮
        self.usb_connect_button = QPushButton(self.centralwidget)
        self.usb_connect_button.setObjectName(u"usb_connect_button")
        self.usb_connect_button.setGeometry(QRect(360, 60, 80, 20))
        # 烧录固件标签
        self.file_label = QLabel(self.centralwidget)
        self.file_label.setObjectName(u"file_label")
        self.file_label.setGeometry(QRect(20, 100, 53, 20))
        # 烧录固件
        self.file_lineEdit = QLineEdit(self.centralwidget)
        self.file_lineEdit.setObjectName(u"file_lineEdit")
        self.file_lineEdit.setGeometry(QRect(80, 100, 260, 20))
        # 烧录固件选择
        self.file_selection_button = QPushButton(self.centralwidget)
        self.file_selection_button.setObjectName(u"file_selection_button")
        self.file_selection_button.setGeometry(QRect(360, 100, 80, 20))
        # 烧录地址标签
        self.base_address_label = QLabel(self.centralwidget)
        self.base_address_label.setObjectName(u"base_address_label")
        self.base_address_label.setGeometry(QRect(20, 140, 140, 20))
        # 烧录地址
        self.base_address_lineEdit = QLineEdit(self.centralwidget)
        self.base_address_lineEdit.setObjectName(u"base_address_lineEdit")
        self.base_address_lineEdit.setGeometry(QRect(160, 140, 180, 20))
        # 是否擦除芯片
        self.chip_erase_checkBox = QCheckBox(self.centralwidget)
        self.chip_erase_checkBox.setObjectName(u"chip_erase_checkBox")
        self.chip_erase_checkBox.setGeometry(QRect(340, 140, 100, 20))
        # 进度条
        self.flash_progressBar = QProgressBar(self.centralwidget)
        self.flash_progressBar.setObjectName(u"flash_progressBar")
        self.flash_progressBar.setGeometry(QRect(20, 180, 320, 20))
        self.flash_progressBar.setValue(0)
        # 烧录按钮
        self.flash_button = QPushButton(self.centralwidget)
        self.flash_button.setObjectName(u"flash_button")
        self.flash_button.setGeometry(QRect(360, 180, 80, 20))
        # 信息标签
        self.logs_label = QLabel(self.centralwidget)
        self.logs_label.setObjectName(u"logs_label")
        self.logs_label.setGeometry(QRect(20, 220, 420, 20))

        # 信号与槽
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

    def retranslateUi(self):
        self.file_selection_button.setText(QCoreApplication.translate("MCUProg", u"选择固件", None))
        self.flash_button.setText(QCoreApplication.translate("MCUProg", u"烧录", None))
        self.usb_connect_button.setText(QCoreApplication.translate("MCUProg", u"连接", None))
        self.target_label.setText(QCoreApplication.translate("MCUProg", u"目标芯片", None))
        self.downloard_label.setText(QCoreApplication.translate("MCUProg", u"烧录器", None))
        self.file_label.setText(QCoreApplication.translate("MCUProg", u"烧录固件", None))
        self.speed_label.setText(QCoreApplication.translate("MCUProg", u"烧录速度", None))
        self.base_address_label.setText(QCoreApplication.translate("MCUProg", u"烧录地址 (bin格式生效)", None))
        # self.base_address_lineEdit.setText(QCoreApplication.translate("MCUProg", u"0x08000000", None))
        self.chip_erase_checkBox.setText(QCoreApplication.translate("MCUProg", u"是否擦除芯片", None))
        

    def usb_selection(self):
        self.usb_probe()

    def target_selection(self):
        self.targets_comboBox.clear()
        list_targets = ListGenerator.list_targets()
        targets = list_targets['targets']
        for target in targets:
            # print(target['name'])
            self.targets_comboBox.addItem(target['name'])

    # def click_install_pack(self):
    #     pack_file_path, _ = QFileDialog.getOpenFileName(self, "选择pack文件",self.file_path or os.getcwd(),'(*.pack)')
    #     print(pack_file_path)
    #     # self.file_lineEdit.setText(self.file_path)

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
                self.logs_label.setText("已断开连接")
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
                                    unique_id=self.Probe.unique_id,
                                    options = {"frequency": self.frequency[self.speed_comboBox.currentText()], 
                                                "target_override": self.targets_comboBox.currentText()})
                if self.session:
                    self.session.open()
                    board = self.session.board
                    print("Board MSG:")
                    print("Board's name:%s" % board.name)
                    print("Board's description:%s" % board.description)
                    print("Board's target_type:%s" % board.target_type)
                    print("Board's unique_id:%s" % board.unique_id)
                    print("Board's test_binary:%s" % board.test_binary)
                    print("Unique ID: %s" % board.unique_id)
                    target = board.target
                    print("Part number:%s" % target.part_number)
                    memory_map = target.get_memory_map()
                    ram_region = memory_map.get_default_region_of_type(MemoryType.RAM)
                    rom_region = memory_map.get_boot_memory()
                    print("menory map: ",memory_map)
                    print("ram_region: ",ram_region)
                    print("rom_region: ",rom_region)
                    self.usb_connect_button.setText("断开")
                    self.usb_comboBox.setEnabled(False)
                    self.logs_label.setText("已连接")

    def progress(self, Value):
        self.flash_progressBar.setValue(Value*100)
        if Value == 1:
            self.logs_label.setText("烧录完成")
        else:
            self.logs_label.setText("烧录中...")

    def programmer_finished(self):
        print("programmer_finished")

    def flash_button_click(self):
        # print("flash_button_click")
        self.flash_progressBar.reset()
        if self.session and self.session.is_open :
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
        about_Dialog.resize(200, 200)
        about_Dialog.setMinimumSize(QSize(200, 200))
        about_Dialog.setMaximumSize(QSize(200, 200))
        about_Dialog.setWindowTitle("关于")
        icon = QIcon(icon_path)
        about_Dialog.setWindowIcon(icon)

        about_label = QLabel(about_Dialog)
        about_label.setObjectName(u"about_label")
        about_label.setGeometry(QRect(0, 0, 200, 200))

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



