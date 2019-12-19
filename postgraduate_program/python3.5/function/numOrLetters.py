# 判断输入的是不是数字
def isNum(text):
    try:
        num = float(text)
    except:
        return False
    else:
        return True
if __name__ == '__main__':
    print(isNum("11.1"))