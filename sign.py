import requests
import os
import smtplib

from email.mime.text import MIMEText

refresh_token = os.environ.get("ALIYUN_REFRESH_TOKEN")

email_user = os.environ.get("EMAIL_USER")
email_pass = os.environ.get("EMAIL_PASS")
email_to = os.environ.get("EMAIL_TO")

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def send_email(subject, content):

    msg = MIMEText(content, "plain", "utf-8")

    msg["Subject"] = subject
    msg["From"] = email_user
    msg["To"] = email_to

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)

    server.login(email_user, email_pass)

    server.sendmail(
        email_user,
        email_to,
        msg.as_string()
    )

    server.quit()

# 获取 token
url = "https://api.aliyundrive.com/v2/account/token"

data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

r = requests.post(url, json=data, headers=headers)

result = r.json()

if "access_token" not in result:

    msg = "❌ 阿里云盘 refresh_token 已失效"

    print(msg)

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

# 新 refresh_token
new_refresh_token = result["refresh_token"]

# 写回 GitHub ENV
with open(os.environ['GITHUB_ENV'], 'a') as f:
    f.write(f"NEW_REFRESH_TOKEN={new_refresh_token}\n")

access_token = result["access_token"]

# 签到
sign_url = "https://member.aliyundrive.com/v1/activity/sign_in_list"

headers2 = {
    "Authorization": f"Bearer {access_token}",
    "User-Agent": "Mozilla/5.0"
}

res = requests.post(
    sign_url,
    json={"isReward": True},
    headers=headers2
)

sign_result = res.json()

if sign_result.get("success"):

    count = sign_result["result"]["signInCount"]

    reward = sign_result["result"]["signInLogs"][count - 1]["reward"]["notice"]

    msg = f"""
✅ 阿里云盘签到成功

📅 本月累计签到：{count} 天

🎁 今日奖励：
{reward}
"""

    print(msg)

    send_email(
        "阿里云盘签到成功",
        msg
    )

else:

    msg = f"""
❌ 阿里云盘签到失败

{sign_result}
"""

    print(msg)

    send_email(
        "阿里云盘签到失败",
        msg
    )
