import requests
import os
import smtplib

from email.mime.text import MIMEText

# =========================
# 配置
# =========================

refresh_token = os.environ.get("ALIYUN_REFRESH_TOKEN")

pushplus_token = os.environ.get("PUSHPLUS_TOKEN")

email_user = os.environ.get("EMAIL_USER")
email_pass = os.environ.get("EMAIL_PASS")
email_to = os.environ.get("EMAIL_TO")

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# =========================
# 邮件通知
# =========================

def send_email(subject, content):

    try:

        msg = MIMEText(content, "plain", "utf-8")

        msg["Subject"] = subject
        msg["From"] = email_user
        msg["To"] = email_to

        server = smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=30
        )

        server.ehlo()

        server.login(email_user, email_pass)

        server.sendmail(
            email_user,
            email_to,
            msg.as_string()
        )

        server.quit()

        print("✅ 邮件发送成功")

    except Exception as e:

        print("❌ 邮件发送失败")
        print(e)

# =========================
# 微信通知
# =========================

def send_wechat(title, content):

    try:

        requests.get(
            "https://www.pushplus.plus/send",
            params={
                "token": pushplus_token,
                "title": title,
                "content": content
            },
            timeout=20
        )

        print("✅ 微信通知发送成功")

    except Exception as e:

        print("❌ 微信通知失败")
        print(e)

# =========================
# 获取 access_token
# =========================

try:

    url = "https://api.aliyundrive.com/v2/account/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=20
    )

    result = r.json()

except Exception as e:

    msg = f"❌ 获取 token 失败\n\n{e}"

    print(msg)

    send_wechat(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

# =========================
# token 失效
# =========================

if "access_token" not in result:

    msg = f"""
❌ refresh_token 已失效

返回内容：

{result}
"""

    print(msg)

    send_wechat(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

# =========================
# 自动更新 refresh_token
# =========================

new_refresh_token = result["refresh_token"]

with open(os.environ['GITHUB_ENV'], 'a') as f:
    f.write(f"NEW_REFRESH_TOKEN={new_refresh_token}\n")

print("✅ refresh_token 已自动更新")

access_token = result["access_token"]

print("✅ access_token 获取成功")

# =========================
# 开始签到
# =========================

try:

    sign_url = "https://member.aliyundrive.com/v1/activity/sign_in_list"

    headers2 = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.post(
        sign_url,
        json={"isReward": True},
        headers=headers2,
        timeout=20
    )

    sign_result = res.json()

except Exception as e:

    msg = f"❌ 签到请求失败\n\n{e}"

    print(msg)

    send_wechat(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

# =========================
# 签到成功
# =========================

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

    send_wechat(
        "阿里云盘签到成功",
        msg
    )

    send_email(
        "阿里云盘签到成功",
        msg
    )

# =========================
# 签到失败
# =========================

else:

    msg = f"""
❌ 阿里云盘签到失败

返回内容：

{sign_result}
"""

    print(msg)

    send_wechat(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )
