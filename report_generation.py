import datetime

import json
import os
import re
import sqlite3
import time
from typing import Any

from docxtpl import DocxTemplate

datebase_name: str = "datebase.db"

# Подключаемся в базе данных
con = sqlite3.connect(datebase_name)
cursor = con.cursor()


def name_day_week(day_week: datetime) -> str:
    """
    Возвращает названия дня недели по дате

    """
    week_name = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    return week_name[datetime.datetime.weekday(day_week)]


def month_names(list_date: list) -> list:
    """
    Возвращает список с именами месяцев дла 3 таблиц (заездов)
    :param list_date:
    :return:
    """

    month_list = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь',
                  'ноябрь', 'декабрь']

    temp_list_month = []
    new_list_month = []

    i = 0
    for item in list_date:
        i += 1
        temp_list_month.append(month_list[int(item.strftime('%m')) - 1])
        if i == 4:
            for item_2 in temp_list_month:
                while temp_list_month.count(item_2) > 1:
                    temp_list_month.remove(item_2)
            new_list_month.append(temp_list_month)
            temp_list_month = []
            i = 0
    temp_list_month = []
    for item in new_list_month:
        if len(item) > 1:
            # print(f'{item[0]} - {item[1]}')
            item_t = f'{item[0]} - {item[1]}'
        else:
            item_t = item[0]
        temp_list_month.append(item_t)
    return temp_list_month


def short_name(teacher: str) -> str:
    """Вернуть инициалы (Фамилия И.О.)"""
    return re.sub(r'(?<= \w)\w+', '.', teacher)


def get_list_school(team_num: int):
    """Получить таблицу список школ по номеру команды"""
    return cursor.execute(f"SELECT * FROM school WHERE team = {team_num}")


def get_list_id_school(team_num: int) -> list:
    """Получить список ID школ по номеру команды
    :param team_num:
    :return:
    """
    response = cursor.execute(f"SELECT * FROM school WHERE team = {team_num}")
    list_id = []
    for item in response:
        list_id.append(item[0])
    return list_id


def get_class_num(school_number: int, group_name: str) -> int:
    """Получить класс группы по номеру школы и имени группы
    :param school_number: Номер школы
    :param group_name: Название группы
    :return: Номер класса этой группы
    """
    cursor.execute(
        f"SELECT class FROM student WHERE school = {school_number} and group_name='{group_name}' GROUP BY class")
    response = cursor.fetchone()
    return int(response[0])
    # for item in response:
    #     return item[0]


def get_list_group_name(school_num: int) -> list[dict[str, int]]:
    """ Получить список групп и индекс по номеру школы
    :param school_num:
    :return: список групп индекс|название группы
    """
    response = cursor.execute(f"SELECT DISTINCT group_name FROM student WHERE school = {school_num} ")
    group_list = []
    for item in response:
        group_list.append(item[0])
    # print('Список всех групп')
    # for item in group_list:
    #     print(item)

    group_dop_list = []

    # Создаем список групп допников
    for i, item in enumerate(group_list):
        if item in ('В-1', 'В-2', 'В-3', 'Р-1', 'Р-2', 'Р-3', 'А-1', 'А-2', 'А-3'):
            group_dop_list.append(item)

    group_dop_list.sort()  # Сначала сортируем по буквам
    group_dop_list.sort(key=lambda x: (int(x.split('-')[1])))  # Потом сортируем по номеру

    # Удаляем допников из основного списка
    for item in ('В-1', 'В-2', 'В-3', 'Р-1', 'Р-2', 'Р-3', 'А-1', 'А-2', 'А-3'):
        while group_list.count(item) > 0:
            group_list.remove(item)

    # print('--- Список групп допников ---')
    # for item in group_dop_list:
    #     print(f'Name = {item}')
    # print('--- Список групп УТ ---')
    #
    # for item in group_list:
    #     print(f'Name = {item}')

    group_list += group_dop_list
    new_list: list[dict[str, int]] = []
    for i, item in enumerate(group_list, 1):
        new_list.append({
            'index': i,
            'name': item})

    # print('---------')
    # for item in new_list:
    #     print(f'Name = {item}')

    return new_list


def time_lesson(index_number_group: int) -> str:
    """
    Возвращает время во сколько проходят занятия у этой группы
    :return: time_lesson:str
    :param index_number_group:
    """
    time_lesson: str = ''
    if index_number_group in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        time_lesson = '11:40 – 14:10'
        print(time_lesson)
    elif index_number_group in [10, 11, 12, 13, 14, 15, 16, 17, 18]:
        time_lesson = '14:10 – 16:40'
        print(time_lesson)
    else:
        print('Ошибка в time_less')
    return time_lesson


def list_day_lesson(index_number_group: int, list_start_date: list) -> list:
    """
    Возвращает список всех учебных дней у группы
    :param
    index_number_group: индекс группы
    list_start_date: список начальных дат заездов
    """
    list_date: list = []
    for item in list_start_date:
        item = datetime.datetime.strptime(item, '%d.%m.%Y')
        if index_number_group in [1, 2, 3, 10, 11, 12]:
            list_date.append(item + datetime.timedelta(days=0))  # Первый день занятий
            list_date.append(item + datetime.timedelta(days=3))  # Второй день
            list_date.append(item + datetime.timedelta(days=7))  # Третий день
            list_date.append(item + datetime.timedelta(days=10))  # Четвертый день
            # print('Понедельник-Четверг')
        elif index_number_group in [4, 5, 6, 13, 14, 15]:
            list_date.append(item + datetime.timedelta(days=1))  # Первый день занятий
            list_date.append(item + datetime.timedelta(days=2))  # Второй день
            list_date.append(item + datetime.timedelta(days=8))  # Третий день
            list_date.append(item + datetime.timedelta(days=9))  # Четвертый день
            # print('Вторник-Среда ')
        elif index_number_group in [7, 8, 9, 16, 17, 18]:
            list_date.append(item + datetime.timedelta(days=4))  # Первый день занятий
            list_date.append(item + datetime.timedelta(days=5))  # Второй день
            list_date.append(item + datetime.timedelta(days=11))  # Третий день
            list_date.append(item + datetime.timedelta(days=12))  # Четвертый день
            # print('Пятница-Суббота')
        else:
            print('Ошибка в list_day_lesson')
    for item in list_date:
        print(name_day_week(item))
    return list_date


def report_gen(team_num: int, school_num: int, group_name: str, class_num: int, index_number_group: int) -> None:
    """Номер команды, номер школы, номер группы, класс, уровень
    :param team_num: (id) Номер команды.
    :param school_num: (id) Номер школы.
    :param group_name: Название группы.
    :param class_num: Номер класса.
    :param index_number_group: Индекс группы.
    """

    # --------------- Создание переменных --------------

    table_list_students = []  # Таблица со списком детей
    table_list_theme_1 = []  # Таблица со списком тем по направлению 1
    table_list_theme_2 = []  # Таблица со списком тем по направлению 2
    table_list_theme_3 = []  # Таблица со списком тем по направлению 3

    table_security_1 = []  # Таблица техники безопасности 1
    table_security_2 = []  # Таблица техники безопасности 1
    table_security_3 = []  # Таблица техники безопасности 1

    list_students: list[Any] = []
    list_start_date: list[Any] = []  # Даты начало заездов
    list_date: list[Any] = []

    safety_precautions = 'Быть внимательным и дисциплинированным. Не размещать посторонние предметы на столах. Не включать компьютеры без разрешения учителя. Не трогать провода и разъемы соединительных кабелей.'

    program_name: str = ''
    teacher_dop: str = ''
    # group_type = ''
    # group: str = ''  # Название группы детей (УТ-1 ВР-2)
    # group_num: int = 0  # Номер группы детей (УТ-1 = 1 УТ-8 = 8)
    # school_num:int = 0 # Номер школы
    teacher_arvr: str = ''  # Имя преподавателя по ARVR
    teacher_geo: str = ''  # Имя преподавателя по ГЕО
    teacher_robo: str = ''  # Имя преподавателя по Робо
    school_name: str = ''  # Название школы

    # --------------- Открытие json --------------------
    with open("list_themes.json", "r", encoding="utf-8") as file:
        list_themes = json.load(file)

    if team_num == 2:
        teacher_arvr = 'Чистяков Илья Сергеевич'
        teacher_geo = 'Мельников Павел Сергеевич'
        teacher_robo = 'Каданова Мария Павловна'
        print(f'Выбрана команда {team_num} - {teacher_arvr}, {teacher_geo}, {teacher_robo}.')

    if team_num == 1:
        teacher_arvr = 'Малкова Татьяна Николаевна'
        teacher_geo = 'Бодров Дмитрий Эдуардович'
        teacher_robo = 'Федосеева Мария Михайловна'
        print(f'Выбрана команда {team_num} - {teacher_arvr}, {teacher_geo}, {teacher_robo}.')

    if team_num == 4:
        teacher_arvr = 'Иванов Егор Владимирович'
        teacher_geo = 'Большаков Александр Алексеевич'
        teacher_robo = 'Киреев Максим Александрович'
        print(f'Выбрана команда {team_num} - {teacher_arvr}, {teacher_geo}, {teacher_robo}.')

    if team_num == 3:
        teacher_arvr = 'Лисенков Алексей Дмитриевич'
        teacher_geo = 'Романов Павел Анатольевич'
        teacher_robo = 'Кушнир Дмитрий Сергеевич'
        print(f'Выбрана команда {team_num} - {teacher_arvr}, {teacher_geo}, {teacher_robo}.')

    # ------------- Формирование дат от выбранной школы -------------

    respond = cursor.execute(f"SELECT * FROM school WHERE id = {school_num}")
    for item in respond:
        school_name = item[1]
        list_start_date = item[2].split(',')

    print(f'Выбрана школа: {school_name} | даты заездов - {list_start_date}')

    # --------------- Формирование списка детей ---------------

    respond = cursor.execute(f'SELECT FIO FROM student WHERE school = {school_num} and group_name = "{group_name}"')

    for item in respond:
        list_students.append(item[0])
    # print(list_students)

    # Время занятий
    lesson_time = time_lesson(index_number_group)

    # Формирование таблицы списка детей
    for item in list_students:
        table_list_students.append({
            'fio_student': item,
            'school_name': school_name
        })

    # Список дат дней всех занятий группы
    list_date = list_day_lesson(index_number_group, list_start_date)

    print(
        f'Выбрана группа {group_name} | {class_num} класс | Начало занятий - {name_day_week(list_date[0]).upper()} | ')

    # ---------- Вывод списка дат
    # for item in list_date:
    #     item = item.strftime('%d.%m.%y')
    #     print(item)

    def table_themes(index_date: int, theme: str, teacher_name: str) -> list:
        """Создать таблицу со списком тем дата|тема|часы|подпись
        :param index_date: индекс дат с которой начинается заполнение темы
        :param theme: название направления
        :param teacher_name: полное имя преподавателя
        :return: table: таблица дата|тема|часы|подпись
        """
        table = []
        hours = 0
        index_date -= 1
        name = short_name(teacher_name)
        for ITEM in list_themes[theme]:
            date_theme = list_date[index_date].strftime('%d/%m')
            # print(date_theme)
            hours += int(ITEM[1])
            # print(f'hours - {hours}')
            if hours == 3:
                index_date += 1
                hours = 0
            table.append({
                'date': date_theme,
                'theme': ITEM[0],
                'hour': ITEM[1],
                'fio': name
            })
        # for item in table:
        #     print(item)

        return table

    def table_security(date: int, teacher_name: str) -> list:
        """Создает таблицу техника безопасности дата|тема|часы|подпись
        :param date:
        :param teacher_name:
        :return:
        """
        name = short_name(teacher_name)
        table = []
        for item in list_students:
            table.append({
                'fio_student': item,
                'date_tb': list_date[date - 1].strftime('%d.%m.%Y'),
                'teacher': name
            })
        return table

    # Находим тип группы в названии группы
    group_type = str(re.search(r'([А-Я]+)', group_name, re.I).group())

    def split_table(table: list) -> object:
        """
        Разделяет темы на 3 таблицы по 12 часов
        :param table:
        :return: таблица 1, таблица 2, таблица 3
        """

        hour = 0
        first_separator = 0
        second_separator = 0
        for i, item in enumerate(table, 1):
            hour += int(item['hour'])
            # print(f'Часы - {hour}')
            if hour == 12:
                first_separator = i
                # print(first_separator)
            if hour == 24:
                second_separator = i
                # print(second_separator)

        table_1 = table[:first_separator]
        table_2 = table[first_separator:second_separator]
        table_3 = table[second_separator:]
        # print(table_1)
        # print(table_2)
        # print(table_3)
        return table_1, table_2, table_3

    # Формируем контент для шаблона
    if group_type == 'УТ':
        # --------------- Открываем шаблон УТ -------------
        template = DocxTemplate('шаблон_УТ.docx')

        if group_name in ('УТ-1', 'УТ-4', 'УТ-7', 'УТ-10', 'УТ-13', 'УТ-16'):
            table_list_theme_1 = table_themes(1, f'List_theme_GEO_{class_num}', teacher_geo)
            table_security_1 = table_security(1, teacher_geo)

            table_list_theme_2 = table_themes(5, f'List_theme_ARVR_{class_num}', teacher_arvr)
            table_security_2 = table_security(5, teacher_arvr)

            table_list_theme_3 = table_themes(9, f'List_theme_Robo_{class_num}', teacher_robo)
            table_security_3 = table_security(9, teacher_robo)

        elif group_name in ('УТ-2', 'УТ-5', 'УТ-8', 'УТ-11', 'УТ-14', 'УТ-17'):
            table_list_theme_1 = table_themes(1, f'List_theme_ARVR_{class_num}', teacher_arvr)
            table_security_1 = table_security(1, teacher_arvr)

            table_list_theme_2 = table_themes(5, f'List_theme_Robo_{class_num}', teacher_robo)
            table_security_2 = table_security(5, teacher_robo)

            table_list_theme_3 = table_themes(9, f'List_theme_GEO_{class_num}', teacher_geo)
            table_security_3 = table_security(9, teacher_geo)

        elif group_name in ('УТ-3', 'УТ-6', 'УТ-9', 'УТ-12', 'УТ-15', 'УТ-18'):
            table_list_theme_1 = table_themes(1, f'List_theme_Robo_{class_num}', teacher_robo)
            table_security_1 = table_security(9, teacher_robo)

            table_list_theme_2 = table_themes(5, f'List_theme_GEO_{class_num}', teacher_geo)
            table_security_2 = table_security(5, teacher_geo)

            table_list_theme_3 = table_themes(9, f'List_theme_ARVR_{class_num}', teacher_arvr)
            table_security_3 = table_security(9, teacher_arvr)

    elif group_type in ('В', 'А', 'Р'):
        # --------------- Открываем шаблон допов -------------
        template = DocxTemplate('шаблон_ДОП.docx')

        if group_name in ('В-1', 'В-2', 'В-3'):
            teacher_dop = teacher_arvr
            program_name = 'Виртуальная реальность и информационные технологии'
            table_list_theme_1, table_list_theme_2, table_list_theme_3 = split_table(
                table_themes(1, f'List_theme_{group_type}', teacher_arvr))

            table_security_1 = table_security(1, teacher_arvr)
            table_security_2 = table_security(5, teacher_arvr)
            table_security_3 = table_security(9, teacher_arvr)

        elif group_name in ('А-1', 'А-2', 'А-3'):
            teacher_dop = teacher_geo
            program_name = 'Геоинформационные технологии и Аэротехнологии. Изучение DJI Rise Tello и Mavic 2 pro'
            table_list_theme_1, table_list_theme_2, table_list_theme_3 = split_table(
                table_themes(1, f'List_theme_{group_type}', teacher_geo))

            table_security_1 = table_security(1, teacher_geo)
            table_security_2 = table_security(5, teacher_geo)
            table_security_3 = table_security(9, teacher_geo)

        elif group_name in ('Р-1', 'Р-2', 'Р-3'):
            teacher_dop = teacher_robo
            program_name = 'Образовательная робототехника на базе Arduino, Makeblock'
            table_list_theme_1, table_list_theme_2, table_list_theme_3 = split_table(
                table_themes(1, f'List_theme_{group_type}', teacher_robo))

            table_security_1 = table_security(1, teacher_robo)
            table_security_2 = table_security(5, teacher_robo)
            table_security_3 = table_security(9, teacher_robo)
        else:
            print(f'Неизвестная группа - {group_name}')
    else:
        print(f'Неизвестная группа - {group_name}')

    # Наполнением контентом
    context = {
        'program_name': program_name,
        'teacher_dop': teacher_dop,
        'lesson_time': lesson_time,
        'table_list_students': table_list_students,
        'table_list_theme1': table_list_theme_1,
        'table_list_theme2': table_list_theme_2,
        'table_list_theme3': table_list_theme_3,
        'table_tb1': table_security_1,
        'table_tb2': table_security_2,
        'table_tb3': table_security_3,
        'teacher_geo': teacher_geo,
        'teacher_arvr': teacher_arvr,
        'teacher_robo': teacher_robo,
        'teacher_GEO_short': short_name(teacher_geo),
        'teacher_ARVR_short': short_name(teacher_arvr),
        'teacher_Robo_short': short_name(teacher_robo),
        'school_name': school_name,
        'class_num': class_num,
        'group_name': group_name,
        'safety_precautions': safety_precautions
    }
    # ------------ Заполнение дат -------------
    for i, item in enumerate(list_date, 1):
        context[f'date_{i}_d'] = str(item.strftime('%d'))
        context[f'date_{i}_y'] = str(item.strftime('%Y'))
        context[f'date_{i}_dm'] = str(item.strftime('%d.%m'))
        context[f'date_{i}_dmy'] = str(item.strftime('%d.%m.%Y'))
        context[f'week_day_{i}'] = name_day_week(item)
    # print(context)

    for i, item in enumerate(month_names(list_date), 1):
        context[f'month_{i}'] = item

    # Render automated Generating_reports_WORD
    template.render(context)

    patch = f'/result/{school_name}/{group_type}'
    try:
        os.makedirs(os.getcwd() + patch)

    except OSError:
        pass
        # print(f"Создать директорию не удалось")
    else:
        print("Успешно создана директория")

    # print(f'{os.getcwd() + patch}/Журнал {group_name}, {school_name}.docx')
    template.save(f'{os.getcwd() + patch}/Журнал {group_name}, {school_name}.docx')
