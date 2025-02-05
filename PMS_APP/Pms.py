import os
import sys
from time import sleep

import pyautogui
from AppOpener.check import app_names

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtGui
from pywinauto import Desktop, Application

from PMS_APP.Pms_ui import Ui_MainWindow
from PMS_APP.common_lib import open_app, click_object, find_object, close_app

#Function load data galaxybook
def load_data_galaxybook():
    try:
        target_window = open_app('Galaxy Book Experience')
        is_see_all = click_object(target_window, "See all", "SeeAll", "Button")
        is_apps_and_services = find_object(target_window, "Apps and services", "SpCardApp", "Group")

        child_elements = is_apps_and_services[2].descendants(control_type="ListItem")
        dic_elements = {
            'app_name': [],
            'status': []
        }
        for element in child_elements:
            element_name = element.descendants(control_type='Pane')[0].window_text()
            if element_name == 'Phone Link' or element_name == 'Phone' or element_name == 'Continue apps on other devices':
                pass
            else:
                element_status = element.descendants(control_type='Button')[0].window_text()
                dic_elements['app_name'].append(element_name)
                dic_elements['status'].append(element_status)

        list_app_name = dic_elements['app_name']
        list_app_status = dic_elements['status']

        return [list_app_name, list_app_status]
    except Exception as e:
        print(f'Load data error: {e}')

#Fucntion check uninstall/ install success
def check_success(app_name, app_status, handle):
    data_galaxybook = load_data_galaxybook()
    if len(data_galaxybook[0]) == len(data_galaxybook[1]):
        for app, status in zip(data_galaxybook[0], data_galaxybook[1]):
            if app == app_name:
                if status != app_status:
                    print(f'{app_name} {handle} success')
                else:
                    print(f'{app_name} {handle} Fail')



#Class threads
class Worker(QThread):
    finished = pyqtSignal() # Signal to indicate the thread is finished

    def __init__(self, target = None):
        super().__init__()
        self.target = target
        self._is_running = True

    def run(self):
        if self.target:
            self.target()
        self.finished.emit() # Emit the signal when the work is done

    def stop(self):
        self._is_running = False

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()

        self.threads = []
        self.app_name_list = []
        self.app_status_list = []

    def init_ui(self):
        global tableView, model

        #Init table
        tableView = self.ui.tableResult
        self.ui.uninstallBtn.clicked.connect(self.on_btn_uninstall_clicked)
        self.ui.installBtn.clicked.connect(self.on_btn_install_clicked)

        num_col = 3
        model = QtGui.QStandardItemModel(0, num_col)
        model.setHorizontalHeaderLabels(['App List', 'Uninstall', 'Install'])
        header = tableView.horizontalHeader()
        header.setDefaultSectionSize(147)

        load_data = load_data_galaxybook()
        app_list = load_data[0]
        for index, app_name in enumerate(app_list):
            item = QtGui.QStandardItem(app_name)
            model.setItem(index, 0, item)

        tableView.setModel(model)

    # Function reinstall app
    def reinstall_app(self, app_name):
        try:
            target_window = open_app('Galaxy Book Experience')
            is_see_all = click_object(target_window, "See all", "SeeAll", "Button")
            is_apps_and_services = find_object(target_window, "Apps and services", "SpCardApp", "Group")

            child_elements = is_apps_and_services[2].descendants(control_type="ListItem")
            for element in child_elements:
                element_focus = element.descendants(control_type='Pane')[0]
                element_install = element.descendants(control_type='Button')[0]
                if element_focus.window_text() == app_name:
                    element_install.click_input()
                    sleep(5)

            store_app = Application(backend='uia').connect(title_re='Microsoft Store')
            store_window = store_app.window(title_re='Microsoft Store')

            isInstall = click_object(store_window, 'Install ', 'InstallOwnedProduct', 'Button')
            if not isInstall[0]:
                isInstall = click_object(store_window, 'Get ', 'AcquireNewProduct', 'Button')
                if not isInstall[0]:
                    isInstall = click_object(store_window, 'Retry ', 'RetryInstallation', 'Button')

            sleep(20)
            close_app('Microsoft Store')
            # app_and_services_text = click_object(target_window, "Apps and services", "AppsAndServices", "Text")
            # check_success(app_name, 'Install', 'Reinstall')
        except Exception as e:
            print(f'reinstall app error: {app_name, e}')

    # Function uninstall app
    def uninstall_app(self, app_name):
        try:
            pyautogui.hotkey('win', 's')

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')

            pyautogui.write(app_name, interval=0.1)
            sleep(2)

            app = Application(backend='uia').connect(title_re='Search')
            target_window = app.window(title_re='Search')

            click_object(target_window, "Uninstall", "pp_Tile.Uninstall", "ListItem")

            click_object(target_window, "Uninstall", "dialog_b0", "Button")
            sleep(5)

            # check_success(app_name, 'Open', 'uninstall')
            # print(target_window.print_control_identifiers())
        except Exception as e:
            print(f"Uninstall app error: {e}")

    # Function click uninstall
    def on_btn_uninstall_clicked(self):
        self.app_name_list = []
        self.app_status_list = []
        self.current_index = 0
        self.ui.installBtn.setEnabled(False)
        data_galaxybook = load_data_galaxybook()
        if len(data_galaxybook[0]) == len(data_galaxybook[1]):
            for app_name, status in zip(data_galaxybook[0], data_galaxybook[1]):
                if status == 'Open':
                    self.app_name_list.append(app_name)
                    self.app_status_list.append(status)
        self.next_app('Uninstall')

    # Function click install
    def on_btn_install_clicked(self):
        self.app_name_list = []
        self.app_status_list = []
        self.current_index = 0
        self.ui.uninstallBtn.setEnabled(False)
        data_galaxybook = load_data_galaxybook()
        if len(data_galaxybook[0]) == len(data_galaxybook[1]):
            for app_name, status in zip(data_galaxybook[0], data_galaxybook[1]):
                if status == 'Install':
                    self.app_name_list.append(app_name)
                    self.app_status_list.append(status)
        self.next_app('Install')
    # Function init test case result
    def init_result(self, row_index):
        global window, tableView
        item = QtGui.QStandardItem('Running')
        model.setItem(row_index, 1, item)
        tableView.setModel(model)
        tableView.viewport().update()

    # Function run next app
    def next_app(self, handle_app):
        if self.current_index < len(self.app_name_list):
            try:
                # Run thread init test case in table
                thread = Worker(target=lambda: self.init_result(self.current_index))
                self.threads.append(thread)
                # Run thread handle
                thread.finished.connect(self.start_handle_app)
                thread.start()
                print(f"Started init_result thread for app name: {self.app_name_list[self.current_index]}")
            except Exception as e:
                print(f'Error click: {e}')

    # Function handle install app
    def start_handle_app(self):
        if self.current_index >= len(self.threads) or not self.threads[self.current_index]._is_running:
            return
        app_name = self.app_name_list[self.current_index]
        app_status = self.app_status_list[self.current_index]
        try:
            # run thread handle_result
            thread = Worker(target=lambda: self.handle_result(app_name, 'Install'))
            self.threads.append(thread)
            thread.finished.connect(self.on_thread_finished)
            thread.start()
            print(f"Started handle_result thread for app name: {self.app_name_list[self.current_index]}")
        except Exception as e:
            print(f'Error handle: {e}')

    # Function handle result
    def handle_result(self, app_name, handle_method):
        try:
            if handle_method == 'Install':
                self.reinstall_app(app_name)
                print(f"install app finish: {app_name}")
            else:
                self.uninstall_app(app_name)
                print(f"install app finish: {app_name}")
        except Exception as e:
            print(f'Lỗi xử lý: {e}')

    # Function finish handle result
    def on_thread_finished(self):
        print(f"Thread for testcase {self.app_name_list[self.current_index]} finished")
        print('current index: ', self.current_index)
        self.current_index += 1
        if self.current_index < len(self.app_name_list):
            self.next_app()
        else:
            self.ui.uninstallBtn.setEnabled(True)
            self.ui.stopBtn.setEnabled(False)

    # Function stop all threads
    def stop_all_threads(self):
        for thread in self.threads:
            thread.stop()
        self.threads.clear()

    # Function stop click
    def on_btn_stop_clicked(self):
        self.stop_all_threads()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
