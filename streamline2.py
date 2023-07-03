# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:05:48 2023

@author: 515142385
"""
# scrcpy --turn-screen-off --disable-screensaver --show-touches --stay-awake --video-codec=h264 --video-bit-rate=10M --max-fps=12
import pyautogui
import pandas as pd
import time
import os
import subprocess
from PIL import Image, ImageGrab, ImageColor
from the_cavities import cavities

shift_keys = "!@#$%^&*()_+~{}:<>?"
root_dir = 'R:/'
CSV_FILE = 'runnit.csv'

image_crop = [90,27,1826,1040]

def ramdisk(status):
    if status == 1:
        os.system(r'start-ramdisk.bat') 
    elif status == 0:
        os.system(r'kill-ramdisk.bat')
    time.sleep(1)

def drag_down_once(sleep=0.5): 
    pyautogui.moveTo(1000,853)
    pyautogui.mouseDown()
    pyautogui.moveTo(1000, 315, duration=0.4)
    pyautogui.mouseUp()
    time.sleep(sleep)
    
def universal_go_back():
    pyautogui.moveTo(500,500)
    pyautogui.rightClick()
    pyautogui.rightClick()
    print('Test failed!, going back to main menu!')
    
    time.sleep(25)

def smart_type(string, hover=''):
    for character in string:
        if character in shift_keys:
            if hover == '':
                tap_to(hover)
            pyautogui.hotkey("shift", character)
            time.sleep(0.07)       
        else:
            pyautogui.typewrite(character)
            time.sleep(0.07)   
               
def check_file(file): 
    print(os.access(file, os.R_OK)) # Check for read access
    print(os.access(file, os.W_OK)) # Check for write access
    print(os.access(file, os.X_OK)) # Check for execution access
    print(os.access(file, os.F_OK)) # Check for existence of file
    
def parse_magic_pixel(mpix):
    coords_color_tol_rel = mpix.split('-')

    coords = coords_color_tol_rel[0]
    hex_color = coords_color_tol_rel[1]
    tolerance = coords_color_tol_rel[2]
    release = coords_color_tol_rel[3]

    coords = coords.split(' ')
    x, y = coords[0], coords[1]
    
    print(x, y, hex_color, tolerance, release)
    
    return  x, y, hex_color, int(tolerance), release
    
def get_coords(cavity):
    coords = cavity.split(' ',1)
    return int(coords[0]), int(coords[1])
         
def execute_test_cases(file):
    file_proper = fr'{file}'
    check_file(file)
    df = pd.read_csv(file_proper, 
                     na_values='nan',
                     keep_default_na=False)
    
    ref_list = list()
    index_list = list()
    
    for i, row in df.iterrows():
        if row['refno'] != 'nan' or row['refno'] != '':
            try:
                ref_list.append(int(str(row['refno']).strip()))
                index_list.append(i)
            except:
                ref_list.append('fake')
                index_list.append('fake')
        
    ref_dict = dict(zip(ref_list,index_list))
    
    # delete the last key that contains 'fake' to only have valid iterable reference numbers
    del ref_dict['fake']
    # ------------------------------------------------------------------
    appended_ref_list = list()
    appended_epic_list = list()
    appended_result_list = list()
    appended_screenshot_list = list()
    # appended_expected_list = list() --> this will be implemented later
    # ------------------------------------------------------------------
    idx = 0
    df_range = len(df)
    print(df_range)
    
    while (idx != df_range):
        
        epic = str(df.loc[idx, 'epic'])  # Will be used for the TTS engine
    
        if epic != '' or epic != 'nan':
            appended_epic_list.append(epic)
    
        cavity = str(df.loc[idx, 'cavity']).strip()
        text = str(df.loc[idx,'text']).strip()
        command = str(df.loc[idx,'command']).strip()
        magic_pixel = str(df.loc[idx,'mPixel']).strip()
        
        try:
            if int(str(df.loc[idx,'refno'])) != '':
                refno = int(str(df.loc[idx,'refno']))
                appended_ref_list.append(refno)
        except:
            pass
            
        print(f'>>>{refno}<<<')
        
        try:
            sleep = float(str(df.loc[idx,'sleep']))
        except:
            sleep = 0.00
        
        if cavity == 'scroll_down':
            drag_down_once(sleep)

        elif cavity == 'tap':
            print('tap is executed')
            pyautogui.click()
            
        elif cavity == 'decomission':
            tap_to(cavities.get('top_right_x_cavity'),1)
            
            for i in range(1,4):
                drag_down_once(0.3)
            time.sleep(1)
            
            # change this to csv
            tap_to((324,822),1)
            tap_to((317,396),1)
            tap_to((1992,658),2)
            tap_to((1205,662),2)
        
        elif cavity == 'get_time':
            pass
            
        else:
            if text == '' or text == 'nan':
                print(f'{idx}. @{cavity} IDLE -> {sleep}s.')
                
                if cavity in cavities:    
                    tap_to(cavities.get(cavity), sleep)
                elif cavity == '':
                    print('NOP') 
                
                else: # line needs some fixing
                    tap_to((get_coords(cavity)), sleep)
            else:
                if cavity in cavities:
                    print(f"{idx}. @{cavity} KEYB -> '{text}'")
                    smart_type(text, cavities.get(cavity))
                elif cavities != '':
                    print(f"{idx}. @{cavity} KEYB -> '{text}'")
                    smart_type(text, (get_coords(cavity)))
                    
        if 'ss' in command:
            split_to_enumerate = command.split(' ',1)
            screenshot = ImageGrab.grab()
            ram_file = root_dir + str(ref_list[-1])
            image = screenshot.crop((image_crop[0],image_crop[1],
                                    image_crop[2],image_crop[3]))
            
            print(f'{ram_file}-{split_to_enumerate[1]}.jpg\n')
            
            image = image.save(f'{ram_file}-{split_to_enumerate[1]}.jpg' ,quality=4)
            appended_screenshot_list.append(image)
         
            # add output to excel sheet here
        if magic_pixel != '':
            x, y, hex_color, tolerance, release = parse_magic_pixel(magic_pixel)
            r, g, b = ImageColor.getcolor(hex_color,"RGB")
            
            print(r,g,b)
            
            time.sleep(0.4)
            screengrab = ImageGrab.grab()
            actual_pixel = screengrab.load()
            
            expected_pixel = (r,g,b)
            
            actual_pixel = tr, tg, tb = actual_pixel[int(x),int(y)]
            
            print(actual_pixel)
            
            # if test pass/fail start
            if  flex_match(expected_pixel,actual_pixel,tolerance) == True and '!' not in release:
                appended_result_list.append(str('PASS'))
                print("TEST PASS!")
                
                # edit spreadsheet cell for pass
            elif flex_match(expected_pixel,actual_pixel,tolerance) == False and '!' not in release:
                appended_result_list.append(str('FAIL'))
                print("TEST FAIL!")
                
                keys_list = list(ref_dict.keys())
                index = keys_list.index(appended_ref_list[-1])
                
                if index < len(keys_list)-1:
                    
                    next_key = keys_list[index+1]
                    next_value = ref_dict[next_key]
                    
                    print(next_value)
                    idx = (next_value - 1) # this line fixes everything jajajajaja
                    
                    print(">>>>>> ", (idx+2)," <<<<<<")
                else:
                    print("There is no next value in the dictionary.")
                
                universal_go_back()

            time.sleep(1)
        
        print("\n")
        idx += 1
        
    while("" in appended_epic_list):
        appended_epic_list.remove("")
    
    return appended_ref_list, appended_epic_list, appended_result_list, appended_screenshot_list
            
def flex_match(expected, actual, tolerance):
    rmax, rmin = expected[0] + tolerance, expected[0] - tolerance
    gmax, gmin = expected[1] + tolerance, expected[1] - tolerance
    bmax, bmin = expected[2] + tolerance, expected[2] - tolerance
    
    actual_r, actual_g, actual_b = actual[0],actual[1],actual[2]
    
    if actual_r in range(rmin,rmax) and actual_g in range(gmin,gmax) and actual_b in range(bmin,bmax):
        return True
    else:
        return False
            
def tap_to(hover, sleep_time = 0): 
    if sleep_time <= 0:
        pyautogui.moveTo(hover)
        pyautogui.click()
    else:
        pyautogui.moveTo(hover)
        pyautogui.click()
        time.sleep(sleep_time)

if __name__ == '__main__':    
    subprocess.Popen('screen.bat')    
    time.sleep(8)  
    
    tap_to((882, 225))
    tap_to((882, 225))
    
    ramdisk(1)
    time.sleep(4)
    tap_to((400, 30),1)
    refs, epics, results, screenshots = execute_test_cases(CSV_FILE)
    
    temp_list = []
    for i in range(len(refs)-len(results)):
        temp_list.append(str('NT'))
        
    results_xt = results.extend(temp_list)
    
    # screenshots_with_idx = list()
    excel_df = pd.DataFrame({
        'reference':refs,
        'epic (test case)':epics,
        'test result': results
        # 'screenshots': screenshots_with_idx # list of lists
        })
    
    with pd.ExcelWriter("test_results.xlsx") as writer:
        excel_df.to_excel(writer)  
        
    ramdisk(0)