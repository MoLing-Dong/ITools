from datetime import datetime, timedelta


def calculate_schedule(start_time, work_hours=12, rest_hours=24):
    """
    计算未来的上下班时间
    :param start_time: 当前下班时间（字符串，格式为 "YYYY-MM-DD HH:MM"）
    :param work_hours: 上班时长（小时）
    :param rest_hours: 休息时长（小时）
    :return: 返回一个列表，包含未来的上下班时间
    """
    # 将输入的时间字符串转换为 datetime 对象
    current_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")

    # 初始化结果列表
    schedule = []

    # 计算未来 5 个班次（可以根据需要调整）
    for i in range(5):
        # 当前班次的下班时间
        off_time = current_time
        # 当前班次的上班时间
        on_time = off_time + timedelta(hours=rest_hours)
        # 下一个班次的下班时间
        next_off_time = on_time + timedelta(hours=work_hours)

        # 将时间添加到结果列表
        schedule.append({
            "班次": i + 1,
            "上班时间": on_time.strftime("%Y-%m-%d %H:%M"),
            "下班时间": next_off_time.strftime("%Y-%m-%d %H:%M")
        })

        # 更新当前时间为下一个班次的下班时间
        current_time = next_off_time

    return schedule


# 输入今天的下班时间
start_time = "2025-10-04 8:00"  # 今天是六点下班

# 计算未来的上下班时间
schedule = calculate_schedule(start_time)

# 打印结果
print("未来的上下班时间：")
for entry in schedule:
    print(f"班次 {entry['班次']}:")
    print(f"  上班时间: {entry['上班时间']}")
    print(f"  下班时间: {entry['下班时间']}")
