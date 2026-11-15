import pymysql

class DBManager:
    # 1. 初始化方法
    def __init__(self,db_config):
        self.conn = pymysql.connect(**db_config)
        self.cursor = self.conn.cursor()

    # 2. 专门负责“查询（SELECT）”的方法
    def execute_query(self,sql,params=None):
        try:
            self.cursor.execute(sql,params)
            return self.cursor.fetchall()  # 返回所有游标查询结果
        except Exception as e:
            print(f"！查询执行失败：{e}")
            return []

    # 3. 专门负责“增删改/建表（INSERT/UPDATE/DELETE）”的方法
    def execute_update(self,sql,params=None):
        try:
            self.cursor.execute(sql,params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"!数据更新失败，已回滚：{e}")
            return False

    # 4. 收尾关闭方法
    def close(self):
        self.cursor.close()
        self.conn.close()

    # 只有直接运行本文件时才会执行下面的测试代码
if __name__ == "__main__":
        from config import DB_CONFIG

        db = DBManager(DB_CONFIG)
        rows = db.execute_query("SELECT * FROM attendance;")
        print("成功查询数据：",rows)
        db.close()
