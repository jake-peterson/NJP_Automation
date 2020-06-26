# Install following libraries in command prompt!!
# pip install pytesseract
# pip install numpy
# pip install PIL

import pytesseract as pyt
import os, sys
import subprocess
import pyautogui as pya
import signal
from PIL import Image
import csv
import numpy as np
import re
import time
import calendar

directory = r'C:\Users\user\OneDrive\Documents\file\name'
csv_directory = r'C:\Users\user\OneDrive\Documents\file\name.csv'
copy_csv = r'C:\Users\user\OneDrive\Documents\file\Previous_name.csv'
#window = win.GetForegroundWindow()

def csvreader(): #open and read current csv to update list and determine next pic to look at
    with open(csv_directory, newline='') as csvfile:
        reader = csv.reader(csvfile)
        values = list(reader)
        if len(values) == 0:
            values.append(['RANCHO','PROYECTO', 'CAMARA', 'REGISTRO','#FOTO','PERIODO','GENERO','ESPECIE','SEXO','HORA','EDAD','# INDIVIDUOS','DIA','MES','ANO','OBSERVACIONES'])
            counter = 0
        else:
            counter = int(values[0][1])
            values = values[1:]
    csvwriter(counter, values, True)
    return counter, values

def csvwriter(k, valuelist, *makecopy): #write updates to csv
    if makecopy:
        with open(copy_csv,'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Counter: ', str(k)])
            writer.writerows(valuelist)
        print ("Previous copy updated!")
    else:
        try:
            with open(csv_directory,'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Counter: ', str(k)])
                writer.writerows(valuelist)
            print ("File updated!")
        except: #if an error occurs dump updates to a new csv file
            with open('new_csv_NJP.csv','w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Counter: ', str(k)])
                writer.writerows(valuelist)
            print ("Error, new file updated!")

def photodetailsfun(im):
    #crop the image so tesseract can read more accurately
    im = im.crop((400,im.size[1]-50,im.size[0],im.size[1]))
    temp = pyt.image_to_string(im).split()
    if len(temp) < 5: #two different type of camreas taking pictures and time/date info is different
        try: #try finding the time if not input
            if temp[1][-2:] == 'AM':
                if int(temp[1][:temp[1].find(':')]) >= 10 and int(temp[1][:temp[1].find(':')]) < 12:
                    hour = inputcheck('hour', temp[1][:-2])
                else:
                    if int(temp[1][:temp[1].find(':')]) == 12:
                        hour = inputcheck('hour', '00' + temp[1][2:-2])
                    else:
                        hour = inputcheck('hour', '0' + temp[1][0:-2])
            else:
                if int(temp[1][:temp[1].find(':')]) == 12:
                    hour = inputcheck('hour', temp[1][:-2])
                else:
                    pmtime = int(temp[1][:temp[1].find(':')]) + 12
                    hour = inputcheck('hour', str(pmtime) + temp[1][-5:-2])
        except:
            hour = inputcheck('hour')
        try: #try finding date if not input
            if int(temp[0].split('/')[0]) < 10: #make sure month has two char
                temp[0] = '0' + temp[0]
            if int(temp[0].split('/')[1]) < 10: #make sure day has two char
                temp[0] = temp[0][:2] + '0' + temp[0][2:]
            if int(temp[0].split('/')[2]) > 99:
                temp[0] = temp[0][:-4] + temp[0][-2:]
            date = inputcheck('date', temp[0])
        except:
            date = inputcheck('date')
    else: #if streamcapture image then use normal time/date
        hour = inputcheck('hour', temp[0])
        date = inputcheck('date', temp[1])
    month = date.split('/')[0]
    day = date.split('/')[1]
    year = date.split('/')[2]
    return (hour, date, day, month, year)

def nextcheck(currentlocation): #check if the user wants to continue, or save progress
    while True:
        if currentlocation == 'Photo': #checks if user wants to go to next pic
            nextpic = input('Continue to next picture (y/n): ')
        if currentlocation == 'Folder': #checks if user wants to go to next folder at end of current folder
            print('\nNew Folder!!!')
            nextpic = input('\n\nContinue to next folder (y/n): ')
        if nextpic in ['y', 'Y', 'n', 'N']: 
            break
        else:
            print('Input must be y or n!')
            continue
    if nextpic in ['Y', 'y']:
        return True
    else:
        return False

def inputcheck(inputtype, *readtime): #check input values on various user inputs
    while True:
        if inputtype == 'individuals': #should only be int
            try:
                temp = int(input('Number of individuals: '))
                break
            except ValueError: 
                print('Input must be an integer!')
                continue
        if inputtype in ['genus', 'species', 'observations']: #should always be over 3 char or unknown
            temp = input('Enter ' + inputtype + ' (if unknown enter u or none): ')
            if temp in ['u', 'U', 'none', 'None']:
                temp = temp.upper()
                break
            if len(temp) > 3:
                break
            else:  
                print('Please provide acceptable input!')
                continue
        if inputtype == 'sex': #should be either male/female or unknown
            temp = input('Enter sex (m or f or u): ')
            if temp in ['m', 'M', 'f', 'F', 'u', 'U']:
                temp = temp.upper()
                break
            else:
                print('Input must be m or f or u!')
                continue
        if inputtype == 'age': #should either be adult/juvenile or unknown
            temp = input('Adult or juvenile? (a or j or u): ')
            if temp in ['a', 'A', 'j', 'J', 'u', 'U']:
                temp = temp.upper()
                break
            else:
                print('Input must be a or j or u!')
                continue
        if inputtype == 'hour': #ensure user inputs correct format
            pattern = re.compile('^[0-9]{2}:[0-9]{2}$')
            if len(readtime) == 0:
                temp = input('What time is on the photo? (14:45): ')
            else:
                temp = str(readtime[0])
            if pattern.match(temp):
                break
            else:
                print('Please use correct format (03:25)!')
                readtime = ''
                continue
        if inputtype == 'date':
            pattern = re.compile('^[0-9]{2}/[0-9]{2}/[0-9]{2}$')
            if len(readtime) == 0:
                temp = input('What date is on the photo? (02/25/19): ')
            else:
                temp = str(readtime[0])
            if pattern.match(temp):
                break
            else:
                print('Please use correct format (03/25/20)!')
                readtime = ''
                continue
    if temp in ['U', 'NONE']:
            temp = ''
    return temp

def periodfinder(ranch, camera, lists):
    count = 0
    smallest = ''
    largest = ''
    lists = np.array(lists, dtype = object)
    for x in lists:
        if x[2] == camera and x[0] == ranch: 
            count += 1
    for x in lists[len(lists) - count:]:
        if x[5] < smallest or smallest == '':
            smallest = x[5]
        if x[5] > largest or largest == '':
            largest = x[5]
    for x in lists[len(lists) - count:]: 
        x[5] = smallest + ' A ' + largest
    lists = lists.tolist()
    return lists

k = 0
check = True
counter, values = csvreader() 

try:
    if check == True:
        for ranch in os.listdir(directory):
            if check == True:
                templocation = directory + '\\' + ranch
                for camera in os.listdir(templocation):
                    folderfilecount = 0
                    if check == True:
                        newtemplocation = templocation + '\\' + camera
                        for photo in os.listdir(newtemplocation):
                            if check == True:
                                folderfilecount += 1
                                if  counter > k:
                                    k += 1
                                    continue
                                else: 
                                    photolocation = newtemplocation + '\\' + photo
                                    im = Image.open(photolocation)
                                    tempshow = subprocess.Popen('"' + photolocation + '" -W -n', shell = True)
                                    time.sleep(1)
                                    pya.hotkey('alt', 'tab')
                                    individuals = inputcheck('individuals')
                                    if individuals != 0:
                                        foto = photo[photo.find('STC_')+4:photo.find('.jpg')]
                                        hour, date, day, month, year = photodetailsfun(im)
                                    for x in range(individuals):
                                        genus = inputcheck('genus')
                                        if genus in ['fox ', 'cow ', 'horse', 'donkey', 'dog ', 'bunny', 'deer', 'coyote', 'racoon', 'ocel', 'bob ', 'jag ', 'lion', 'pig ', 'turkey']:
                                            if genus == 'fox ':
                                                genus = 'Urocyon'
                                                species = 'cinereoargenteus'
                                            if genus == 'cow ':
                                                genus = 'Bos '
                                                species = 'taurus'
                                            if genus == 'horse':
                                                genus = 'Equus'
                                                species = 'caballus'
                                            if genus == 'donkey':
                                                genus = 'Equus'
                                                species = 'asinus'
                                            if genus == 'dog ':
                                                genus = 'Canis'
                                                species = 'familiaris'
                                            if genus == 'bunny':
                                                genus = 'Sylvilagus'
                                                species = 'floridanus'
                                            if genus == 'deer':
                                                genus = 'Odocoileus'
                                                species = 'virginianus'
                                            if genus == 'coyote':
                                                genus = 'Canis'
                                                species = 'latrans'
                                            if genus == 'racoon':
                                                genus = 'Procyon'
                                                species = 'lotor'
                                            if genus == 'ocel':
                                                genus = 'Leopardus'
                                                species = 'pardalis'
                                            if genus == 'bob ':
                                                genus = 'Lynx'
                                                species = 'rufus'
                                            if genus == 'jag ':
                                                genus = 'Panthera'
                                                species = 'onca'
                                            if genus == 'lion':
                                                genus = 'Puma'
                                                species = 'concolor'
                                            if genus == 'pig ':
                                                genus = 'Pecari'
                                                species = 'tajacu'  
                                            if genus == 'turkey':
                                                genus = 'Meleagris'
                                                species = 'gallopavo'   
                                        elif genus == 'repe':
                                            genus = values[-1][6]
                                            species = values[-1][7]
                                        else:
                                            species = inputcheck('species')
                                        sex = inputcheck('sex')
                                        age = inputcheck('age')
                                        observations = inputcheck('observations')
                                        values.append([ranch, 'FF', camera, 'Fotografia', foto, date, genus, species, sex, hour, age, individuals, day, calendar.month_name[int(month)], year, observations])
                                    if folderfilecount == len(os.listdir(newtemplocation)):
                                        check = nextcheck('Folder')
                                        values = periodfinder(ranch, camera, values)
                                    else:
                                        check = nextcheck('Photo')
                                    im.close()
                                    os.system('taskkill /f /im  Microsoft.Photos.exe 1>nul 2>&1')
                                    k += 1
                            else:
                                break
                    else:
                        break    
            else:
                break
except Exception as e:
    print(e)

csvwriter(k, values)




