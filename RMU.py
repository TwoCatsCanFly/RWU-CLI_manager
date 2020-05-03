'''
Hi this app is for GOG RimWorld mod updating
using steam mods directory.
'''
'''
добавить поддержку языка
добавить выбор целевой и конечной папки
добавить выбор модификации
добавить второй уровень меню с действия ми для конкретного мода
добавить инфо о зависимостях
'''


import os,time
game = 'RimWorld'

txt_list = {0:'Версия игры в целевой папке: ',
            1:'Версия игры в папке Steam: ',
            5:'       Автор: ',
            6:'       Версия: ',
            7:'       Поддерживает версии: ',
            'q':'Выход из программы',
            'errinp':'Некоректный ввод',
            'wip':'Функция в разработке'}
menu = ['1. Догрузить недостающие моды в целевую папку WIP',
        '2. Догрузить все моды в целевую папку WIP',
        '3. Список модов установленных через Steam',
        '4. Список модов установленных вручную',
        '5. Список всех модов',
        '6. Сравнение списка модов из папки Steam и целевой папки',
        'Q. Выход',]

mods_in_steam_folder = 0
mods_in_rimworld_folder = 0
mods_names_and_folders_steam = 0
mods_names_and_folders_manual = 0

def my_timer(f): #гикбренс лол)))
    def tmp(*args, **kwargs):
        start_time=time.time()
        result=f(*args, **kwargs)
        delta_time=time.time() - start_time
        print ('Время выполнения функции {}' .format(delta_time))
        return result

    return tmp

def version(a,p):
    # a : Папка где хранится директория игры
    # p : 0 Это текст для целевой папки, 1 Для папки Steam
    try:
        with open('{0}\\{1}\Version.txt'.format(a,game)) as ver:
            for line in ver:
                try: print('{}{}'.format(txt_list[p],line),end='')
                except: print("Ошибка словаря")
    except:
        print('Ошибка чтения директории')
        return 0
def xmlp(adr,tag='',li=False):
    # adr - адрес xml\txt файла
    # tag - искомый тег
    # li - является ли искомый тег списком
    import xml.etree.cElementTree as ET
    if adr.endswith('.xml'):
        try:
            ModMetaData = ET.parse(adr)
            if li == False:
                param = ModMetaData.find(tag)
                return param.text
            else:
                param = ModMetaData.findall(tag+'/li')
                ver =[]
                for i in param:
                    a = i.text
                    b = a.split()
                    b = ''.join(b)
                    ver.append(b)
                return ver
        except: return 0
    elif adr.endswith('.txt'):
        try:
            with open(adr) as txt:
                for line in txt:
                    return line
        except: return 0
def about(a,l=0,c=False):
    # a - адрес папки c модом
    # c - Вывод в консоль
    # l - уровень информации:
        # 0 - название
        # 1 - автор
        # 2 - версия
        # 3 - поддерживаемые версии
        # 4 - Идентификатор мода в Steam
        # 5 - название,автор
        # 6 - название,автор,версия
        # 7 - название,автор,версия,поддерживаемые версии
        # 8 - название,автор,версия,поддерживаемые версии, идентификатор мода в Steam
    about = a+'/About/About.xml'
    manifest = a+'/About/Manifest.xml'
    steamid = a+'/About/PublishedFileId.txt'
    if c == True:
        print(('{0}{4}{1}{5}{2}{6}{3}'.format(xmlp(about,'name'),
                                        xmlp(about,'author'),
                                        xmlp(manifest, 'version'),
                                        xmlp(about,'supportedVersions',True),
                                        txt_list[5],
                                        txt_list[6],
                                        txt_list[7])))
    if l == 0: return xmlp(about,'name')
    elif l == 1: return xmlp(about, 'author')
    elif l == 2: return xmlp(manifest, 'version')
    elif l == 3:
        sup_ver = xmlp(about,'supportedVersions', True)
        target_ver = xmlp(about,'targetVersion')
        if target_ver:
            sup_ver.append(target_ver)
        return sup_ver
    elif l == 4: return xmlp(steamid)
    elif l == 5: return [xmlp(about,'name'),xmlp(about,'author')]
    elif l == 6: return [xmlp(about,'name'),xmlp(about,'author'),xmlp(manifest, 'version')]
    elif l == 7:
        sup_ver = xmlp(about,'supportedVersions', True)
        target_ver = xmlp(about,'targetVersion')
        if target_ver:
            sup_ver.append(target_ver)
        return [xmlp(about,'name'),xmlp(about,'author'),xmlp(manifest, 'version') ,sup_ver]
    elif l == 8:
        sup_ver = xmlp(about,'supportedVersions', True)
        target_ver = xmlp(about,'targetVersion')
        if target_ver:
            sup_ver.append(target_ver)
        return [xmlp(about,'name'),xmlp(about,'author'),xmlp(manifest, 'version') ,sup_ver, xmlp(steamid)]
    else:
        print('Ошибка атрибута уровня информации')
        return 0
def scanner(directory,info_level=8):
    count_steam = 0
    count_manual = 0
    mod_list = []
    mod_list_steam = []
    mod_list_manual = []
    folder_and_name = []
    for mods in os.listdir(directory):
        d = '{}\{}'.format(directory, mods)
        j = about(d, 8)
        mod_list.append(j)
        if  j[0]==j[1]==j[2]==j[3]==j[4]==0:
            continue
        if j[4] != 0:
            count_steam += 1
            mod_list_steam.append(j)
        if j[4] == 0:
            count_manual += 1
            mod_list_manual.append(j)
        folder_and_name.append([j[0], d])
    if info_level==0: return count_steam
    elif info_level==1: return count_manual
    elif info_level==2: return [count_steam,count_manual]
    elif info_level==3: return mod_list_steam
    elif info_level==4: return mod_list_manual
    elif info_level==5: return mod_list
    elif info_level==6: return folder_and_name
    elif info_level==7: return [mod_list_steam, mod_list_manual, folder_and_name]
    elif info_level==8: return [count_steam, count_manual, mod_list_steam, mod_list_manual, folder_and_name]
    else: return 0

@my_timer
def modlist(info_level):
    # возвращает инфу ввиде [количество модов,[список модов]]
    steam_directory = scanner(steam_mods)
    rw_directory = scanner(rw_manual)
    if info_level == 0: # Установлено через Steam
        modslist = [steam_directory[0]+rw_directory[0],steam_directory[2]+rw_directory[2]]
        return modslist
    elif info_level == 1: #Установлено вручную
        modslist = [steam_directory[1]+rw_directory[1],steam_directory[3]+rw_directory[3]]
        return modslist
    elif info_level == 2:#Установлено через Steam+вручную
        modslist = [steam_directory[0]+rw_directory[0]+steam_directory[1]+rw_directory[1],steam_directory[2]+rw_directory[2]+steam_directory[3]+rw_directory[3]]
        return modslist
    else: return 0
def corrector(list=0,value_1=0,value_2='default'):
    if value_2 == 'default':
        try:
            something = list[value_1]
            return something
        except: return ''
    else:
        try:
            something = list[value_1][value_2]
            return something
        except: return ''
def printlist(list=0,list_type=0):
    if list_type == 0: # Обычный список модов
        print("%-4s%-70s%-10s%-50s%-25s%-10s" % ('№','Название мода', 'Версия', 'Автор', 'Поддержка версий', 'Steam ID'))
        print('-'*170)
        for id,mods in enumerate(list[1],1):
            try: verinfo = ', '.join(mods[3])
            except: verinfo = '0'
            try: print("%-4s%-70s%-10s%-50s%-25s%-10s" % (id, mods[0], mods[2], mods[1], verinfo, mods[4]))
            except: return 0
    elif list_type == 1: # Сравнительный список модов
        print("%-4s%-70s%-10s%2s%-4s%-70s%-10s" % ('№','Название мода', 'Steam ID','|', '№', 'Название мода', 'Steam ID'))
        print(('-' * 85) + '|' + ('-' * 84))
        a,b,c = [],[],[]
        #q = mods_in_steam_folder[0]
        #f = t
        for id, mods in enumerate(mods_in_steam_folder,1):
            a.append([id,mods[0],mods[4]])
        for id, mods in enumerate(mods_in_rimworld_folder,1):
            b.append([id,mods[0],mods[4]])
        if len(a)>=len(b):
            for i in range(len(a)):
                c.append([corrector(a,i,0),corrector(a,i,1),corrector(a,i,2),corrector(b,i,0),corrector(b,i,1),corrector(b,i,2)])
        else:
            for i in range(len(b)):
                c.append([corrector(a,i,0),corrector(a,i,1),corrector(a,i,2),corrector(b,i,0),corrector(b,i,1),corrector(b,i,2)])
        for i in c:
            print("%-4s%-70s%-10s%2s%-4s%-70s%-10s" % (i[0],i[1],i[2],'|',i[3],i[4],i[5]))

    elif list_type == 2:
        pass
    elif list_type == 3:
        pass
    else: return 0
def mainmenuprint(menu):
    print('_' * 170)
    for i in menu:
        print(i)
    print('_' * 170)
def foldercopy():





    pass
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



steam_mods = 'C:\Games\SteamLibrary\steamapps\workshop\content\\294100'
steam_game_dir = 'C:\Games\SteamLibrary\steamapps\common'
gog = 'C:\Games'
rw_manual = gog+'\\'+game+'\Mods'
allinfo = update()

version(gog,0)
version(steam_game_dir,1)
mainmenuprint(menu)
inputmanager()

