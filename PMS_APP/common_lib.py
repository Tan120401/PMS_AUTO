import codecs
import os
import time
from datetime import datetime
from time import sleep
import subprocess

import pyautogui
from AppOpener import open
from pywinauto import Application, Desktop

def write_log_setting(testcase_name,pass_list, fail_list):
    # Open log file and write
    try:
        result_of_testcase = []
        with codecs.open(f"{log_file_name}", "a", "utf-8") as file:
            file.write(f"*{testcase_name.upper()}\n")
            file.write("-List of pass: ")
            file.write(", ".join(pass_list))
            file.write("\n")
            if len(fail_list) > 0:
                result_of_testcase.append(f"-{testcase_name}: Fail")
                file.write("-List of fail: ")
                file.write(", ".join(fail_list))
                file.write("\n")
            else:
                result_of_testcase.append(f"-{testcase_name}: Pass")
    except Exception as e:
        print(f'Write log error: {e}')

# Function init log file
def init_log_file():
    # change_global_log_file()
    now = datetime.now()
    current_time = now.strftime('%m%d%Y_%H%M%S')
    print(current_time)
    global log_file_name
    log_file_name = f"{current_time}_UIT_LOG.txt"

    # check setting log exists
    if os.path.exists(log_file_name):
        try:
            # delete file
            os.remove(log_file_name)
            print(f"Deleted existing log file: {log_file_name}")
            return log_file_name
        except Exception as e:
            print(f"Error deleting log file: {e}")
    try:
        # Khởi tạo lại file log
        with codecs.open(log_file_name, "w", "utf-8") as file:
            file.write("")  # Tạo file rỗng
        print(f"Initialized new log file: {log_file_name}")
        return log_file_name
    except Exception as e:
        print(f"Error initializing log file: {e}")

# Function to check if objects exist
def base_setting(testcase_name, app_name, dic_object_list):
    try:
        # Open app settings
        target_window = open_app(f"{app_name}")
        # Change title, control type, auto_id, object_handle to List
        titles = dic_object_list['title'].split(', ')
        control_types = dic_object_list['control_type'].split(', ')
        auto_ids = dic_object_list['auto_id'].split(', ')
        object_handles = dic_object_list['object_handle'].split(', ')

        # The List contains the pass fail objects
        pass_list = []
        fail_list = []
        # Check that the lengths of the lists match
        if len(titles) == len(control_types) == len(auto_ids) == len(object_handles):
            for title, auto_id, control_type, object_handle in zip(titles, auto_ids, control_types, object_handles):
                object_result =[]
                if object_handle == 'click':
                    object_result = click_object(target_window, title, auto_id, control_type)
                elif object_handle == 'view':
                    object_result = find_object(target_window, title, auto_id, control_type)
                elif object_handle == 'scroll':
                    scroll_center(target_window, title, auto_id, control_type)
                    object_result = find_object(target_window, title, auto_id, control_type)
                if object_result[0]:
                    pass_list.append(title)
                else:
                    fail_list.append(title)
        else:
            print("Dic object list not match")

        write_log_setting(testcase_name, pass_list, fail_list)
        # close window
        close_app('Settings')

        if len(fail_list) > 0:
            return False
        elif len(pass_list) >0:
            return True
    except Exception as e:
        print(f'Base setting error: {e}')

# Move to object and scroll
def scroll_center(target_window, title, auto_id, control_type):
    try:
        scroll_bar = target_window.child_window(title=title, auto_id=auto_id, control_type=control_type)
        scroll_bar_rec = scroll_bar.rectangle()
        pyautogui.moveTo(scroll_bar_rec.left + 20, scroll_bar_rec.top - 20)
        sleep(1)
        pyautogui.scroll(-800)
        sleep(1)
        return scroll_bar
    except Exception as e:
        print(f'Scroll error: {e}')

# Function close app
def close_app(app_name):
    try:
        app = Application(backend='uia').connect(title_re=app_name)
        target_window = app.window(title_re=app_name)
        target_window.close()
    except Exception as e:
        print(f'close app error: {e}')

# Function open app return target windows
def open_app(app_name):
    try:
        # app_is_open = False
        all_window_active = Desktop(backend='uia').windows()
        for win in all_window_active:
            if win.window_text() == app_name:
                app_is_open = True
                close_app(app_name)
        # if app_is_open:
        #     close_app(app_name)
        #     open(app_name, match_closest=False)
        #     app = Application(backend='uia').connect(title_re=app_name)
        #     target_window = app.window(title_re=app_name)
        # else:
        open(app_name, match_closest=False)
        sleep(3)
        app = Application(backend='uia').connect(title_re=app_name)
        target_window = app.window(title_re=app_name)
        return target_window
    except Exception as e:
        print(f'open app error: {e}')

def wait_until(timeout, interval, condition):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    raise TimeoutError("Time out error")

# Function click object exist
def click_object(window, title, auto_id, control_type):
    object_select = window.child_window(title=title, auto_id=auto_id, control_type=control_type)
    try:
        wait_until(5, 1, lambda: object_select.exists())
        object_select.click_input()
        result = [True, title, object_select]
        # print(window.print_control_identifiers())
    except TimeoutError as e:
        print(f'Click error: {title, e}')
        result = [False, title, None]
    sleep(1)
    return result

# Function find object
def find_object(window, title, auto_id, control_type):
    object_find = window.child_window(title=title, auto_id=auto_id, control_type=control_type)
    try:
        wait_until(5, 0.5, lambda: object_find.exists())
        result = [True, title, object_find]
    except Exception as e:
        print(f'Find Object error: {title, e}')
        result = [False, title, None]
    return result

# Function click object by coordinates
def click_object_by_coordinates(left, top, right, bottom):
    # Define BoundingRectangle
    bounding_rectangle = {'l': left, 't': top, 'r': right, 'b': bottom}

    # Calculate the central coordinates
    center_x = (bounding_rectangle['l'] + bounding_rectangle['r']) // 2
    center_y = (bounding_rectangle['t'] + bounding_rectangle['b']) // 2

    # Move to the central coordinates and click
    pyautogui.moveTo(center_x, center_y)
    pyautogui.click()

# Function to find open windows
def find_open_window(app):
    # List all window
    try:
        all_window_active = Desktop(backend='uia').windows()
        is_app = False
        for win in all_window_active:
            if win.window_text() == app:
               is_app = True
               sleep(2)
               win.close()
        return is_app
    except Exception as e:
        print(f'Find app is open error: {e}')

# Function connected Wi-Fi
def get_connected_wifi():
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"])
        result = result.decode("utf-8", errors="ignore")
        for line in result.split('\n'):
            if "SSID" in line:
                ssid = line.split(":")[1].strip()
                return ssid
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function click element in group
def click_object_within_group(group, name, auto_id, control_type):
    # get all element
    child_elements = group.descendants(control_type=control_type)
    # find elements
    for element in child_elements:
        if element.window_text() == name and element.automation_id() == auto_id:
            return element.click_input()
    return False
