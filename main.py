from report_generation import *

# report_gen(3, 7, 'УТ-2', 5, 2)

# print(get_list_group_name(8))
#
# for item in get_list_group_name(4):
#     print(item['index'])
#     print(item['name'])


team_num: int = 0
group: str = ''
id_school: int = 0

start = time.time()
for team_num in [1, 2, 3, 4]:
    for id_school in get_list_id_school(team_num):
        if id_school not in [4]:
            for group in get_list_group_name(id_school):
                class_num = get_class_num(id_school, group['name'])
                report_gen(team_num, id_school, group['name'], class_num, group['index'])
print(f'время работы программы {float(time.time()-start)}')
