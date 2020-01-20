"""
@File:exer2.py
@Author:lcx
@Date:2020/1/1320:06
@Desc:
"""
def comm(cur, conn):
    insert = "INSERT INTO `waterfall_data_usrp2_1578916891`(`id`,`data_path`) VALUES ('1111','222222')"
    print(insert)
    cur.execute(insert)
    conn.commit()