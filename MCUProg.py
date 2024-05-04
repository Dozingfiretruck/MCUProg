import sys,os
from PySide6.QtWidgets import QFileDialog, QApplication, QMainWindow
from pyocd.core.helpers import ConnectHelper
from pyocd.core.target import Target
from pyocd.core.memory_map import MemoryType
from pyocd.coresight.cortex_m import CortexM
from pyocd.flash.file_programmer import FileProgrammer
from pyocd.tools.lists import ListGenerator
from MCUProg_ui import Ui_MainWindow

class MainWindow(QMainWindow):
    file_path = ''
    allProbes = None
    Probe = None
    session = None
    frequency = {'10MHZ':10000000,'5MHZ':5000000,'2MHZ':2000000,'1MHZ':1000000,'500kHZ':500000,'200kHZ':200000,'100kHZ':100000,'50kHZ':50000,'20kHZ':20000,'10kHZ':10000,'5kHZ':5000}
    def __init__(self, parent = None) :
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.file_selection_button.clicked.connect(self.file_selection_button_click)
        self.ui.usb_connect_button.clicked.connect(self.usb_connect_button_click)
        self.ui.flash_button.clicked.connect(self.flash_button_click)
        self.ui.usb_comboBox.pop_up.connect(self.usb_selection)
        self.ui.speed_comboBox.addItems(['10MHZ','5MHZ','2MHZ','1MHZ','500kHZ','200kHZ','100kHZ','50kHZ','20kHZ','10kHZ','5kHZ'])
        self.usb_probe()
        list_targets = ListGenerator.list_targets()
        pyocd_version = list_targets['pyocd_version']
        targets = list_targets['targets']
        print(pyocd_version) 
        for target in targets:
            # print(target['name'])
            self.ui.targets_comboBox.addItem(target['name'])

    def usb_selection(self):
        self.usb_probe()
        
    def file_selection_button_click(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择下载文件",self.file_path or os.getcwd(),'(*.bin *.hex *.elf *.axf)')
        self.ui.file_lineEdit.setText(self.file_path)
    def usb_connect_button_click(self):
        print("usb_connect_button_click")
        if self.ui.usb_comboBox.currentText():
            if self.session and self.session.is_open:
                self.session.close()
                self.ui.usb_connect_button.setText("连接")
                self.ui.usb_comboBox.setEnabled(True)
            else:
                for Probe in self.allProbes:
                    if self.ui.usb_comboBox.currentText() == Probe.description:
                        self.Probe = Probe
                        break
                # print(self.ui.usb_comboBox.currentText())
                print(Probe,Probe.unique_id)
                # print(self.ui.targets_comboBox.currentText())
                # print(self.frequency[self.ui.speed_comboBox.currentText()])
                if self.Probe:
                    self.session = ConnectHelper.session_with_chosen_probe(blocking=False, return_first=False, unique_id=self.Probe.unique_id,options = {"frequency": self.frequency[self.ui.speed_comboBox.currentText()], "target_override": self.ui.targets_comboBox.currentText()})
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
                    self.ui.usb_connect_button.setText("断开")
                    self.ui.usb_comboBox.setEnabled(False)
    def progress(self, Value):
        self.ui.flash_progressBar.setValue(Value*100)
    def flash_button_click(self):
        print("flash_button_click")
        self.ui.flash_progressBar.reset()
        if self.session and self.session.is_open :
            board = self.session.board
            target = board.target
            # Load firmware into device.
            FileProgrammer(self.session,chip_erase="auto",smart_flash=False,trust_crc=False,keep_unwritten=True,no_reset=True,progress = self.progress).program(self.file_path)
            # Reset
            target.reset_and_halt()

    def usb_probe(self):
        self.allProbes = ConnectHelper.get_all_connected_probes(False, None, False)
        self.ui.usb_comboBox.clear()
        if self.allProbes is None or len(self.allProbes) == 0:
            print("No Probe",self.allProbes)
        else:
            # print(self.allProbes)
            for Probe in self.allProbes:
                print(Probe)
                print(Probe.description)
                print(Probe.unique_id)
                self.ui.usb_comboBox.addItem(Probe.description)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setWindowTitle("MCUProg")
    win.show()
    app.exit(app.exec())



