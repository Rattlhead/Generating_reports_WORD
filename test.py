from typing import List, Any

from report_generation import *

response = cursor.execute(f"SELECT DISTINCT group_name FROM student WHERE school = 2 ")
group_list = []
for item in response:
    group_list.append(item[0])
print('Список всех групп')
for item in group_list:
    print(item)

# group_list = sorted(group_list, key=group_namber)

group_dop_list: list[str] = []

# Создаем список групп допников
for i, item in enumerate(group_list):
    if item in ('В-1', 'В-2', 'В-3', 'Р-1', 'Р-2', 'Р-3', 'А-1', 'А-2', 'А-3'):
        group_dop_list.append(item)

group_dop_list.sort() # Сначала сортируем по буквам
group_dop_list.sort(key=lambda x: (int(x.split('-')[1])))  # Потом сортируем по номеру

# Удаляем допников из основного списка
for item in ('В-1', 'В-2', 'В-3', 'Р-1', 'Р-2', 'Р-3', 'А-1', 'А-2', 'А-3'):
    while group_list.count(item) > 0:
        group_list.remove(item)

print('--- Список групп допников ---')
for item in group_dop_list:
    print(f'Name = {item}')
print('--- Список групп УТ ---')

for item in group_list:
    print(f'Name = {item}')

group_list += group_dop_list
new_list = []
for i, item in enumerate(group_list, 1):
    new_list.append({
        'index': i,
        'name': item})

print('---------')
for item in new_list:
    print(f'Name = {item}')
