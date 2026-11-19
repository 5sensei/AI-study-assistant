from openai import OpenAI
from config import LLM_CONFIG,DB_CONFIG
from db_manager import DBManager
from data_pipeline import analyze_attendance

# 初始化大模型客户端
client = OpenAI(
    api_key=LLM_CONFIG["api_key"],
    base_url=LLM_CONFIG["base_url"]
)

# 1. 核心业务函数：将学生画像打包喂给大模型，生成诊断建议
def generate_study_plan(name,major,late_count,score,risk_level):
    prompt = f"""
    请你扮演一位经验丰富的大学AI导师，根据学生的成绩{name},专业{major},迟到次数{late_count},成绩{score},
    以及学生的风险等级{risk_level},给出3条具体，可执行的学业与考勤改进建议。"""

    try:
        response = client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role":"system","content":"你是你是一个专业、耐心、善于数据分析的大学学业辅导助手。"},
                {"role":"user","content":prompt}
            ],
            temperature=0.7 #创造力温度计（0.0，1.0），当设成0.0时，AI很死板每次都给一模一样的标准答案，适合做数学题，0.7是经典黄金平衡点
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI诊断生成失败：{e}"

# 新增函数 2：将生成的 AI 报告写入 MySQL 数据库
def save_report_to_db(name,major,risk_level,advice):
    # 实例化大管家
    db = DBManager(DB_CONFIG)
    sql = """
    INSERT INTO ai_reports (student_name, major, risk_level, advice)
    VALUES (%s, %s, %s, %s);
    """
    db.execute_update(sql,(name,major,risk_level,advice))
    db.close()
    print(f"✅ 【{name}】的 AI 诊断报告已成功存入 MySQL 数据库！")


# 3. 模块化独立测试入口（串联第 2 车间与第 3 车间）
if __name__ == "__main__":  # 如果运行的是当前文件就跑下边缩进的所有代码
    alert_df = analyze_attendance()
    high_risk_df = alert_df[alert_df["risk_level"] == "高风险"]
    print(f"共检测到{len(high_risk_df)}名高风险学生，正在召唤AI生成一对一诊断报告...\n")

    # 逐行遍历高风险学生，调用 AI 生成建议
    for index, row in high_risk_df.iterrows(): # highriskdf是二维表，上面的generateplan函数一次只能接受5个信息，为了把信息传过去，遍历表，第一轮，index为1，row是第一行一整行的数据。
        print(f"============== 【{row['name']}】学期诊断报告 ==============")
        plan = generate_study_plan(
            name=row["name"],
            major=row["major"],
            late_count=row["late_count"],
            score=row["score"],
            risk_level=row["risk_level"]
        )
        print(plan)
        if not plan.startswith("AI诊断生成失败"):
            save_report_to_db(
                name=row["name"],
                major=row["major"],
                risk_level=row["risk_level"],
                advice=plan
            )
        print("\n")

