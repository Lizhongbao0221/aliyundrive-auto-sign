import requests
import os
import smtplib
import json
import base64
import time

from datetime import datetime
from email.mime.text import MIMEText

# =========================
# 开始时间
# =========================

start_time = datetime.now()

print(f"🚀 开始运行时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

start_timestamp = time.time()

# =========================
# 配置
# =========================

refresh_token = os.environ.get("ALIYUN_REFRESH_TOKEN")

serverchan_key = os.environ.get("SERVERCHAN_SENDKEY")

email_user = os.environ.get("EMAIL_USER")
email_pass = os.environ.get("EMAIL_PASS")
email_to = os.environ.get("EMAIL_TO")

github_token = os.environ.get("GH_TOKEN")
github_repo = os.environ.get("GITHUB_REPOSITORY")

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

        # QQ邮箱 SMTP
        server = smtplib.SMTP_SSL(
            "smtp.qq.com",
            465,
            timeout=30
        )

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
# Server酱通知
# =========================

def send_serverchan(title, content):

    try:

        requests.post(
            f"https://sctapi.ftqq.com/{serverchan_key}.send",
            data={
                "title": title,
                "desp": content
            },
            timeout=20
        )

        print("✅ Server酱通知成功")

    except Exception as e:

        print("❌ Server酱通知失败")
        print(e)

# =========================
# 更新 GitHub Secret
# =========================

def update_github_secret(secret_name, secret_value):

    try:

        url = f"https://api.github.com/repos/{github_repo}/actions/secrets/public-key"

        headers_auth = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json"
        }

        r = requests.get(url, headers=headers_auth)

        public_key = r.json()["key"]
        key_id = r.json()["key_id"]

        from nacl import encoding, public

        public_key_obj = public.PublicKey(
            public_key.encode("utf-8"),
            encoding.Base64Encoder()
        )

        sealed_box = public.SealedBox(public_key_obj)

        encrypted = sealed_box.encrypt(
            secret_value.encode("utf-8")
        )

        encrypted_value = base64.b64encode(encrypted).decode("utf-8")

        put_url = f"https://api.github.com/repos/{github_repo}/actions/secrets/{secret_name}"

        data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id
        }

        requests.put(
            put_url,
            headers=headers_auth,
            data=json.dumps(data)
        )

        print("✅ refresh_token 已自动更新")

    except Exception as e:

        print("❌ GitHub Secret 更新失败")
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

    msg = f"""
❌ 获取 token 失败

🕒 开始时间：
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

错误信息：
{e}
"""

    print(msg)

    send_serverchan(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

if "access_token" not in result:

    msg = f"""
❌ refresh_token 已失效

🕒 开始时间：
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

返回信息：
{result}
"""

    print(msg)

    send_serverchan(
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

update_github_secret(
    "ALIYUN_REFRESH_TOKEN",
    new_refresh_token
)

access_token = result["access_token"]

print("✅ access_token 获取成功")

# =========================
# 签到
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

    msg = f"""
❌ 签到失败

🕒 开始时间：
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

错误信息：
{e}
"""

    print(msg)

    send_serverchan(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )

    exit()

# =========================
# 成功
# =========================

if sign_result.get("success"):

    count = sign_result["result"]["signInCount"]

    reward = sign_result["result"]["signInLogs"][count - 1]["reward"]["notice"]

    end_time = datetime.now()

    duration = round(time.time() - start_timestamp, 2)

    msg = f"""
✅ 阿里云盘签到成功

🕒 开始时间：
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

🏁 结束时间：
{end_time.strftime('%Y-%m-%d %H:%M:%S')}

⏱ 运行耗时：
{duration} 秒

📅 本月累计签到：
{count} 天

🎁 今日奖励：
{reward}
"""

    print(msg)

    send_serverchan(
        "阿里云盘签到成功",
        msg
    )

    send_email(
        "阿里云盘签到成功",
        msg
    )

# =========================
# 失败
# =========================

else:

    end_time = datetime.now()

    duration = round(time.time() - start_timestamp, 2)

    msg = f"""
❌ 阿里云盘签到失败

🕒 开始时间：
{start_time.strftime('%Y-%m-%d %H:%M:%S')}

🏁 结束时间：
{end_time.strftime('%Y-%m-%d %H:%M:%S')}

⏱ 运行耗时：
{duration} 秒

返回信息：
{sign_result}
"""

    print(msg)

    send_serverchan(
        "阿里云盘签到失败",
        msg
    )

    send_email(
        "阿里云盘签到失败",
        msg
    )
