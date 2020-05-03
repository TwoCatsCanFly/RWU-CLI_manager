import os, time, re
import xml.etree.cElementTree as ET
import pandas as pd
import string
from textwrap import TextWrapper as TW
start_time = time.time()
game = 'RimWorld'

txt_list = {'gog': 'Версия игры в целевой папке: ',
            'steam': 'Версия игры в папке Steam: ',
            5: '       Автор: ',
            6: '       Версия: ',
            7: '       Поддерживает версии: ',
            'q': 'Выход из программы',
            'errinp': 'Некоректный ввод',
            'wip': 'Функция в разработке'}

menu = ['1. Догрузить недостающие моды в целевую папку WIP',
        '2. Догрузить все моды в целевую папку WIP',
        '3. Список модов установленных через Steam',
        '4. Список модов установленных вручную',
        '5. Список всех модов',
        '6. Сравнение списка модов из папки Steam и целевой папки',
        'Q. Выход', ]

df = {'steam_mods': 'C:/Games/SteamLibrary/steamapps/workshop/content/294100',
      'steam_game_dir': 'C:/Games/SteamLibrary/steamapps/common/RimWorld',
      'target_directory': 'C:/Games/RimWorld',
      'mods_directory': '/Mods',
      'about': '/About/About.xml',
      'manifest': '/About/Manifest.xml',
      'steam_id': '/About/PublishedFileId.txt',
      'version': '/Version.txt'}

deepness_levels = {1:['supportedVersions','loadAfter','targetVersions','loadBefore'],
                   15:['descriptionsByVersion'],
                   2:['modDependencies','dependencies','incompatibleWith'],
                   25:['loadAfterByVersion'],
                   3:['modDependenciesByVersion']}

def my_timer(f):  # гикбренс лол)))
    def tmp(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        delta_time = time.time() - start_time
        print('Время выполнения функции {} {}'.format(f,delta_time))
        return result
    return tmp

def xmlp(adress):
    def go_deeper(root, tag, deepness_level):
        parsed = {}
        if deepness_level == 1:
            list = []
            for b in root.iterfind('./' + tag + '//'):
                list.append(b.text)
            parsed.update({tag: list})
        elif deepness_level == 15:
            list = {}
            for b in root.iterfind('./' + tag + '/'):
                list.update({b.tag: b.text})
            parsed.update({tag: list})
        elif deepness_level == 2:
            list = {}
            for id, b in enumerate(root.iterfind('./' + tag + '/'), 1):
                adder_list = {}
                for c in root.iterfind('./' + tag + '/' + b.tag + '/'):
                    adder_list.update({c.tag: c.text})
                list.update({id: adder_list})
            parsed.update({tag: list})
        elif deepness_level == 25:
            list = {}
            for b in root.iterfind('./' + tag + '/'):
                adder_list = {}
                for id, c in enumerate(root.iterfind('./' + tag + '/' + b.tag + '/'), 1):
                    for j in root.iterfind('./' + tag + '/' + b.tag + '/'):
                        half_adder_value = j.text
                    adder_list.update({id: half_adder_value})
                list.update({b.tag: adder_list})
            parsed.update({tag: list})
        elif deepness_level == 3:
            list = {}
            for b in root.iterfind('./' + tag + '/'):
                adder_list = {}
                for id, c in enumerate(root.iterfind('./' + tag + '/' + b.tag + '/'), 1):
                    half_adder_list = {}
                    for j in root.iterfind('./' + tag + '/' + b.tag + '/' + c.tag + '/'):
                        half_adder_list.update({j.tag: j.text})
                    adder_list.update({id: half_adder_list})
                list.update({b.tag: adder_list})
            parsed.update({tag: list})
        return parsed
    def string_reaper(string):
        try:
            string.replace('\n','')
            string.replace('\r','')
            string.replace('\t','')
            return string
        except Exception as err:
            return 'Error_string_reaper: {}'.format(err)
    try:
        if adress.endswith('.xml'):
            parsed = {}
            ModMetaData = ET.ElementTree(file=adress)
            root = ModMetaData.getroot()
            for i in root.iterfind('./'):
                if i.tag in deepness_levels[1]:
                    list = go_deeper(root,i.tag,1)
                    parsed.update(list)
                elif i.tag in deepness_levels[15]:
                    list = go_deeper(root,i.tag,15)
                    parsed.update(list)
                elif i.tag in deepness_levels[2]:
                    list = go_deeper(root, i.tag, 2)
                    parsed.update(list)
                elif i.tag in deepness_levels[25]:
                    list = go_deeper(root, i.tag, 25)
                    parsed.update(list)
                elif i.tag in deepness_levels[3]:
                    list = go_deeper(root, i.tag, 3)
                    parsed.update(list)
                else: parsed.update({i.tag:i.text})
            return parsed
        elif adress.endswith('.txt'):
            parsed = {}
            try:
                with open(adress) as txt:
                    for line in txt:
                        str_line = string_reaper(line)
                        parsed.update({re.findall(r'(\w+)\.', adress)[0]: str_line})
                return parsed
            except Exception as err:
                return {'Error_txt': [err, adress]}
        else: return {'Error_inp': 'Unknown input'}
    except:return False

def about(mod_directory):
    total_info = {}
    a,b,c = xmlp(mod_directory + df['about']),xmlp(mod_directory + df['manifest']),xmlp(mod_directory + df['steam_id'])
    if a:
        total_info.update(a)
        total_info.update({'directory': mod_directory})
    if b: total_info.update(b)
    if c: total_info.update(c)
    if a: return total_info
    else: return False

def scanner(mods_directory):
    scanned_list = []
    for mods in os.listdir(mods_directory):
        a = about('{}\{}'.format(mods_directory, mods))
        if a: scanned_list.append(a)
    return scanned_list

def version(game_directory):
    try:
        with open('{}\{}'.format(game_directory,df['version'])) as ver:
            for id,line in enumerate(ver):
                if id == 0: return line
                else: return '0'
    except Exception as err: print('Error_version: {}'.format(err))

def print_list(first_list,second_list=0):
    if second_list==0:
        print("%-4s%-70s%-10s%-50s%-25s%-10s" % ('№','Название мода', 'Версия', 'Автор', 'Поддержка версий', 'Steam ID'))
        print('-'*170)
        for id, mods in enumerate(first_list,1):
            version_list = []
            version_dict = mods.setdefault('supportedVersions')
            target_version = mods.setdefault('targetVersion')
            if version_dict:
                for i in version_dict:
                    version_list.append(i)
            if target_version: version_list.append(target_version)
            ver = ', '.join(version_list)
            print("%-4s%-70s%-10s%-50s%-25s%-10s" % (id, mods.setdefault('name'), mods.setdefault('version'), mods.setdefault('author'), ver, mods.setdefault('PublishedFileId')))
    else:
        print("%-4s%-70s%-10s%2s%-4s%-70s%-10s" % ('№','Название мода', 'Steam ID','|', '№', 'Название мода', 'Steam ID'))
        print(('-' * 85) + '|' + ('-' * 84))
        f_list = {}
        s_list = {}
        for id,mods in enumerate(first_list): f_list.update({id:{'name':mods.setdefault('name'),'PublishedFileId':mods.setdefault('PublishedFileId')}})
        for id,mods in enumerate(second_list): s_list.update({id:{'name':mods.setdefault('name'),'PublishedFileId':mods.setdefault('PublishedFileId')}})
        max_len = max([len(f_list),len(s_list)])
        for i in range(max_len):
            a,b = f_list.setdefault(i,{}),s_list.setdefault(i,{})
            c = {'name_one':a.setdefault('name',''),'PublishedFileId_one':a.setdefault('PublishedFileId',''),'name_two':b.setdefault('name',''),'PublishedFileId_two':b.setdefault('PublishedFileId','')}
            print("%-4s%-70s%-10s%2s%-4s%-70s%-10s" % (i+1, c['name_one'], c['PublishedFileId_one'], '|', i+1, c['name_two'], c['PublishedFileId_two']))




#test = about('C:\Games\RimWorld\Mods\Test')
#print(a['supportedVersions'])
#v = version(df['steam_game_dir'])
a = scanner('C:/Games/SteamLibrary/steamapps/workshop/content/294100')
b = scanner('{}{}'.format(df['target_directory'],df['mods_directory']))
print_list(a,b)


















delta_time = time.time() - start_time
print('----------------------------------------------')
print('Время выполнения кода {} секунд.'.format(round(delta_time,3)))

# -------------------------------------------------------------------------------
'''                for i in param:
                    a = i.text
                    b = a.split()
                    b = ''.join(b)
                    ver.append(b)
                return ver'''

'''
def inputmanager():
    while True:
        i = input('Ввод: ')
        if i == 'Q' or i == 'q' or i == 'й' or i == 'Й':
            print(txt_list['q'])
            quit()
        elif i == '1': print(txt_list['wip'])
        elif i == '2': print(txt_list['wip'])
        elif i == '3':
            j = modlist(0)
            print('_' * 170)
            print('{} Модов в Steam - [{}] {}'.format('-'*4,j[0],'-'*140))
            printlist(j)
            mainmenuprint(menu)
        elif i == '4':
            j = modlist(1)
            print('_' * 170)
            print('{} Модов установленных вручную - [{}] {}'.format('-'*4,j[0],'-'*134))
            printlist(j)
            mainmenuprint(menu)
        elif i == '5':
            j = modlist(2)
            print('{} Всего модификаций - [{}] {}'.format('-'*4,j[0],'-'*136))
            printlist(j)
            mainmenuprint(menu)
        elif i == '6':
            print('_' * 170)
            print("%-4s%-70s%-10s%2s%-4s%-70s%-10s" % ('', 'Установлено в папке Steam', '', '|', '', 'Установлено в папке Rimworld', ''))
            mods_names_and_folders_steam = dict(scanner(steam_mods, 6))
            mods_names_and_folders_manual = dict(scanner(rw_manual, 6))
            mods_in_steam_folder = scanner(steam_mods, 5)
            mods_in_rimworld_folder = scanner(rw_manual, 5)
            print(mods_names_and_folders_steam)
            print(mods_names_and_folders_manual)
            print(mods_in_steam_folder)
            print(mods_in_rimworld_folder)
            printlist(0,1)
            mainmenuprint(menu)
        elif i == '7':
            update()
            print(txt_list['wip'])
        elif i == '8': print(txt_list['wip'])
        else: print(txt_list['errinp'])
        continue
def update():
    #[mods_in_steam_folder, mods_names_and_folders_steam, mods_in_rimworld_folder, mods_names_and_folders_manual]
    return [scanner(steam_mods, 5), dict(scanner(steam_mods, 6)), scanner(rw_manual, 5), dict(scanner(rw_manual, 6))]

'''
