import os
import sys
from time import sleep

import pyautogui
from AppOpener.check import app_names

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt6 import QtGui, QtWidgets
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
def check_success(app_name, app_status):
    data_galaxybook = load_data_galaxybook()
    if len(data_galaxybook[0]) == len(data_galaxybook[1]):
        for app, status in zip(data_galaxybook[0], data_galaxybook[1]):
            if app == app_name:
                if status != app_status:
                    return 'PASS'
                else:
                    return 'FAIL'

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
        self.current_index = 0

    def init_ui(self):
        global tableView, model

        #Init table
        tableView = self.ui.tableResult
        self.ui.uninstallBtn.clicked.connect(self.on_btn_uninstall_clicked)
        self.ui.installBtn.clicked.connect(self.on_btn_install_clicked)
        self.ui.stopBtn.clicked.connect(self.on_btn_stop_clicked)
        self.ui.stopBtn.setEnabled(False)

        num_col = 3
        model = QtGui.QStandardItemModel(0, num_col)
        model.setHorizontalHeaderLabels(['App name', 'Uninstall', 'Install'])
        header = tableView.horizontalHeader()
        header.setDefaultSectionSize(152)

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
            result = check_success(app_name, 'Install')
            return result
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
            result = check_success(app_name, 'Open')
            return result
            # print(target_window.print_control_identifiers())
        except Exception as e:
            print(f"Uninstall app error: {e}")

    # Function show notifications
    def show_notification(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Thông báo")
        msg.setText(message)
        msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f0f0f0;
                        font-size: 14px;
                        min-width: 500px;
                        min-height: 150px;
                    }
                    QMessageBox QLabel {
                        color: #2c3e50;
                    }
                    QMessageBox QPushButton {
                        background-color: #3498db;
                        color: #ffffff;
                        border-radius: 5px;
                        padding: 5px 10px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
        msg.exec()

    # Function click uninstall
    def on_btn_uninstall_clicked(self):
        self.clear_table_data()
        self.app_name_list = []
        self.app_status_list = []
        self.current_index = 0
        self.ui.uninstallBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        data_galaxybook = load_data_galaxybook()
        if len(data_galaxybook[0]) == len(data_galaxybook[1]):
            for app_name, status in zip(data_galaxybook[0], data_galaxybook[1]):
                if status == 'Open':
                    self.app_name_list.append(app_name)
                    self.app_status_list.append(status)
        if len(self.app_name_list) == 0:
            self.show_notification('All app has been uninstalled!')
        else:
            self.next_app('Uninstall')

    # Function click install
    def on_btn_install_clicked(self):
        self.clear_table_data()
        self.app_name_list = []
        self.app_status_list = []
        self.current_index = 0
        self.ui.installBtn.setEnabled(False)
        self.ui.stopBtn.setEnabled(True)
        data_galaxybook = load_data_galaxybook()
        if len(data_galaxybook[0]) == len(data_galaxybook[1]):
            for app_name, status in zip(data_galaxybook[0], data_galaxybook[1]):
                if status == 'Install':
                    self.app_name_list.append(app_name)
                    self.app_status_list.append(status)
        if len(self.app_name_list) == 0:
            self.show_notification('All app has been installed!')
        else:
            self.next_app('Install')

    # Function clear table data
    def clear_table_data(self):
        global model
        for row in range(model.rowCount()):
            model.setData(model.index(row, 1), '')
            model.setData(model.index(row, 2), '')

    # Function init test case result
    def init_uninstall_result(self):
        global window, tableView
        app_name = self.app_name_list[self.current_index]
        item = QtGui.QStandardItem(app_name)
        model.setItem(self.current_index, 0, item)

        item = QtGui.QStandardItem('Running')
        model.setItem(self.current_index, 1, item)
        tableView.setModel(model)
        tableView.viewport().update()

    # Function init test case result
    def init_install_result(self):
        print('init ínstall')
        global window, tableView
        app_name = self.app_name_list[self.current_index]
        item = QtGui.QStandardItem(app_name)
        model.setItem(self.current_index, 0, item)

        item = QtGui.QStandardItem('Running')
        item.setForeground(QtGui.QBrush(QtGui.QColor("blue")))
        model.setItem(self.current_index, 2, item)

        tableView.setModel(model)
        tableView.viewport().update()

    # Function run next app
    def next_app(self, handle_method):
        if self.current_index < len(self.app_name_list):
            try:
                if handle_method == 'Install':
                    # Run thread init test case in table
                    thread = Worker(target=self.init_install_result)
                    self.threads.append(thread)
                    # Run thread handle
                    thread.start()
                    thread.finished.connect(lambda: self.start_handle_method(handle_method))
                    print(f"Started init_install_result thread for app name: {self.app_name_list[self.current_index]}")
                else:
                    # Run thread init test case in table
                    thread = Worker(target=self.init_uninstall_result)
                    self.threads.append(thread)
                    # Run thread handle
                    thread.finished.connect(lambda: self.start_handle_method(handle_method))
                    thread.start()
                    print(f"Started init_uninstall_result thread for app name: {self.app_name_list[self.current_index]}")
            except Exception as e:
                print(f'Error click: {e}')

    # Function handle install app
    def start_handle_method(self, handle_method):
        print('handle')
        if self.current_index >= len(self.threads) or not self.threads[self.current_index]._is_running:
            return
        app_name = self.app_name_list[self.current_index]
        app_status = self.app_status_list[self.current_index]
        try:
            # run thread handle_result
            thread = Worker(target=lambda: self.handle_result(app_name, handle_method))
            self.threads.append(thread)
            thread.finished.connect(lambda: self.on_thread_finished(handle_method))
            thread.start()
            print(f"Started handle_result thread for app name: {self.app_name_list[self.current_index]}")
        except Exception as e:
            print(f'Error handle: {e}')

    # Function reload row data
    def reload_row_data(self, result, row_index, col_index):
        global window, tableView
        item = QtGui.QStandardItem(f'{result}')
        if result.lower() == 'pass':
            item.setForeground(QtGui.QBrush(QtGui.QColor("green")))
        elif result.lower() == 'fail':
            item.setForeground(QtGui.QBrush(QtGui.QColor("red")))
        model.setItem(row_index, col_index, item)
        tableView.setModel(model)

    # Function handle result
    def handle_result(self, app_name, handle_method):
        try:
            if handle_method == 'Install':
                result = self.reinstall_app(app_name)
                self.reload_row_data(result, self.current_index, 2)
                print(f"install app finish: {app_name}")
            else:
                result = self.uninstall_app(app_name)
                self.reload_row_data(result, self.current_index, 1)
                print(f"uninstall app finish: {app_name}")
        except Exception as e:
            print(f'Lỗi xử lý: {e}')

    # Function finish handle result
    def on_thread_finished(self, handle_method):
        print(f"Thread for testcase {self.app_name_list[self.current_index]} finished")
        print('current index: ', self.current_index)
        self.current_index += 1
        if self.current_index < len(self.app_name_list):
            self.next_app(handle_method)
        else:
            if handle_method == 'Install':
                self.show_notification('Successfully installed all apps!')
                self.ui.installBtn.setEnabled(True)
                self.ui.stopBtn.setEnabled(False)
            else:
                self.show_notification('Successfully uninstalled all apps!')
                self.ui.uninstallBtn.setEnabled(True)
                self.ui.stopBtn.setEnabled(False)

    # Function stop all threads
    def stop_all_threads(self):
        print('stop')
        for thread in self.threads:
            thread.stop()
        self.threads.clear()

    # Function stop click
    def on_btn_stop_clicked(self):
        self.stop_all_threads()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""QPushButton { background-color: grey; color: white;}
                      QTableView { background-color: white; color: black;}
                      """)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
