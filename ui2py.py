import os

ui_list = [i.replace('.ui', '') for i in os.listdir() if '.ui' in i]

for ui in ui_list:
    os.system("pyuic5 -x {file_name}.ui -o {file_name}.py".format(file_name=ui))
