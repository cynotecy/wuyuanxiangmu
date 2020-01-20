import os
path1 = r"D:\Program Files\OneDrive - bupt.edu.cn\项目\五院项目资料\集成源码\干扰对消\spectrum_950_1050_4.txt"
path2 = r"D:\Program Files\OneDrive - bupt.edu.cn\项目\五院项目资料\集成源码\干扰对消\direction1.txt"
path3 = r"D:\Program Files\OneDrive - bupt.edu.cn\项目\五院项目资料\集成源码\干扰对消\direction2.txt"
with open(path1, 'r') as f:
    lines = f.readlines()
with open(path2, 'w') as f2:
    f2.write(lines[0])
    f2.write(lines[1])
with open(path3, 'w') as f3:
    f3.write(lines[4])
    f3.write(lines[5])
