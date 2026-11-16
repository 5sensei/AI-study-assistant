import pandas as pd
from config import DB_CONFIG
from db_manager import DBManager

# 1. 业务规则函数：给单个学生评定风险等级
def evaluate_risk(row):
    score = row["score"]
    late_count = row["late_count"]
    if score < 60 or late_count >=3:
        return "高风险"
    elif score<75 or late_count >=1:
        return "中风险"
    else:
        return "正常"

# 2. 核心分析流水线函数
def analyze_attendance():
    db = DBManager(DB_CONFIG)
    # 调用函数去查询表
    sql = "SELECT name, major, late_count, score FROM attendance;"
    rows = db.execute_query(sql)
    db.close()
    # 没查到就返回空的DataFrame
    if not rows:
        return pd.DataFrame()
    # 查出来的rows转成数据，columns指定列名
    df = pd.DataFrame(rows,columns = ["name", "major", "late_count", "score"])
    # 新增一列显示风险等级
    df["risk_level"] = df.apply(evaluate_risk,axis=1)
    alert_df = df[df["risk_level"] != "正常"]
    return alert_df

# 3. 模块化独立测试入口
if __name__ == "__main__":
    result_df = analyze_attendance()
    print("=== 学情风险预警名单 ===")
    print(result_df)