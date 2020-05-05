import os, time, re
import xml.etree.cElementTree as ET
from distutils.util import strtobool
import pandas as pd
#import string
#from textwrap import TextWrapper as TW


game = 'RimWorld'
lang_pack = {'text':{'RU':{'inp':'\nВвод: ',
                            'q': '\nВыход из программы',
                            'errinp': 'Некоректный ввод',
                            'wip': '\nФункция в разработке',
                            'settings':'Доступные параметры:',
                            'param_name':'Введите номер параметра для изменения: ',
                            'param_value':'Изменить параметр на ',
                            'err_param':'Недопустимый параметр',
                            'available_param':'Возможные параметры',
                            'gog':'Версия игры в целевой папке: ',
                            'steam':'Версия игры в папке Steam: ',
                            'about':'Это консольный модменеджер для RimWorld.\nПредназначен для просмотра списков модов и для \nперекидывания модов из Стима в папку RimWorld\nАвтор: CCF'}},
             'menu':{'RU':{'main':{'1':'Догрузить недостающие моды в целевую папку',
                                   '2':'Догрузить все моды в целевую папку',
                                   '3':'Список модов установленных через Steam',
                                   '4':'Список модов установленных вручную',
                                   '5':'Список всех модов',
                                   '6':'Сравнение списка модов из папки Steam и целевой папки',
                                   'U':'Обновить списки',
                                   'S':'Настройки',
                                   'Q':'Q. Выход'},
             'back_to_main':{'m':'Вернутся в главное меню'}}}}
app_settings = {'1':{'language':'RU'},
                '2':{'steam_mods': 'C:/Games/SteamLibrary/steamapps/workshop/content/294100'},
                '3':{'steam_game_dir': 'C:/Games/SteamLibrary/steamapps/common/RimWorld'},
                '4':{'target_directory': 'C:/Games/RimWorld'},
                '5':{'mods_directory': '/Mods'},
                '6':{'about': '/About/About.xml'},
                '7':{'manifest': '/About/Manifest.xml'},
                '8':{'steam_id':'/About/PublishedFileId.txt'},
                '9':{'version': '/Version.txt'},
                '10':{'sort_reversed':'False'},
                '11':{'sort_tag':'name'}}
available_settings = {'language':['RU'],
                      'steam_mods': 'Anything',
                      'steam_game_dir': 'Anything',
                      'target_directory': 'Anything',
                      'mods_directory': 'Anything',
                      'about': 'Anything',
                      'manifest': 'Anything',
                      'steam_id': 'Anything',
                      'version': 'Anything',
                      'sort_reversed': ['False','True'],
                      'sort_tag': ['name','author']
                      }
txt_list = lang_pack['text'][app_settings['1']['language']]
menu_txt = lang_pack['menu'][app_settings['1']['language']]
deepness_levels = {1:['supportedVersions','loadAfter','targetVersions','loadBefore'],
                   15:['descriptionsByVersion'],
                   2:['modDependencies','dependencies','incompatibleWith'],
                   25:['loadAfterByVersion'],
                   3:['modDependenciesByVersion']}
main_lists = {'Steam':None,
              'Manual':None,
              'Steam_dlc':None,
              'Manual_dlc':None,
              'game_versions':[]}

def about_program():
    print('-'*80)
    print(txt_list['about'])
    print('-'*80+'\n')
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
def menu(menu_lines):
    for line in menu_lines:
        print('{}. {}'.format(line,menu_lines[line]))
def wip():
    print(txt_list['wip'])
def wrong_input():
    print(txt_list['errinp'])
def settings(inp):
    if inp not in ['S', 's', 'ы', 'Ы']: return False
    clear()
    while True:
        print(txt_list['settings'])
        for i in app_settings:
            for line in app_settings[i]:
                print('{}. {}: {}'.format(i, line, app_settings[i][line]))
        print('\n')
        menu(menu_txt['back_to_main'])
        i = input(txt_list['param_name'])
        if i in ['m','M','ь','Ь']:
            clear()
            menu(menu_txt['main'])
            break
        if app_settings.get(i)!=None:
            param = []
            for j in app_settings[i]: param.append(j)
            print('{}: {}'.format(txt_list['available_param'],available_settings[param[0]]))
            while True:
                b = input(txt_list['param_value'])
                if b in available_settings[j] or available_settings[j]=='Anything':
                    app_settings[i].update({j:b})
                    break
                if b in ['m','M','ь','Ь']: break
                else:
                    print(txt_list['err_param'])
                    continue

        clear()
        continue

    #else: return False
def quit_program(inp):
    if inp in ['Q','q','й','Й']:
        print(txt_list['q'])
        quit()
    else:return False
def app_main():
    while True:
        i = input(txt_list['inp'])
        if quit_program(i)!=False:continue
        elif settings(i)!=False:continue

        elif menu_1(i)!=False:continue
        elif menu_2(i)!=False:continue
        elif menu_3(i)!=False:continue
        elif menu_4(i)!=False:continue
        elif menu_5(i)!=False:continue
        elif menu_6(i)!=False:continue
        elif menu_update(i)!=False:continue

        else:
            wrong_input()
            continue
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
                        parsed.update({re.findall(r'(\w+)\.', adress)[0]: int(str_line)})
                return parsed
            except Exception as err:
                return {'Error_txt': [err, adress]}
        else: return {'Error_inp': 'Unknown input'}
    except:return False
def about(mod_directory):
    total_info = {}
    a,b,c = xmlp(mod_directory + app_settings['6']['about']),xmlp(mod_directory + app_settings['7']['manifest']),xmlp(mod_directory + app_settings['8']['steam_id'])
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
        with open('{}\{}'.format(game_directory,app_settings['9']['version'])) as ver:
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
def sort_list(list):
    try:
        a = sorted(list, key=lambda x: x[app_settings['11']['sort_tag']],reverse=(strtobool(app_settings['10']['sort_reversed'])))
        return a
    except Exception as err:
        print(err)
        return list
def update():
    start_time = time.time()
    main_lists['Steam'] = scanner('{}'.format(app_settings['2']['steam_mods']))
    main_lists['Manual'] = scanner('{}{}'.format(app_settings['4']['target_directory'], app_settings['5']['mods_directory']))
    main_lists['game_versions'].append(version(app_settings['3']['steam_game_dir']))
    main_lists['game_versions'].append(version(app_settings['4']['target_directory']))
    delta_time = time.time() - start_time
    print('Списки обновлены за {} сек.'.format(round(delta_time, 3)))

def menu_1(input):
    if input == '1': wip()
    else: return False
def menu_2(input):
    if input == '2': wip()
    else: return False
def menu_3(input):
    if input == '3':
        print_list(sort_list(main_lists['Steam']))
        print('\n')
        menu(menu_txt['main'])
    else: return False
def menu_4(input):
    if input == '4':
        print_list(sort_list(main_lists['Manual']))
        print('\n')
        menu(menu_txt['main'])
    else: return False
def menu_5(input):
    if input == '5':
        tot = main_lists['Steam']+main_lists['Manual']

        print_list(sort_list(tot))
    else: return False
def menu_6(input):
    if input == '6':
        print_list(sort_list(main_lists['Steam']),sort_list(main_lists['Manual']))
        print('\n')
        menu(menu_txt['main'])
    else: return False
def menu_update(input):
    if input in ['U','u','г','Г']:
        update()
    else: return False


about_program()
update()
menu(menu_txt['main'])
app_main()

# -------------------------------------------------------------------------------