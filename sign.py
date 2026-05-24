import requests
import os

refresh_token = os.environ.get("ALIYUN_REFRESH_TOKEN")

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# 获取新 token
url = "https://api.aliyundrive.com/v2/account/token"

data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

r = requests.post(url, json=data, headers=headers)

result = r.json()

if "access_token" not in result:
    print("❌ refresh_token 已失效")
    exit()

# 新 token
new_refresh_token = result["refresh_token"]

# 输出给 GitHub Actions
with open(os.environ['GITHUB_ENV'], 'a') as f:
    f.write(f"NEW_REFRESH_TOKEN={new_refresh_token}\n")

access_token = result["access_token"]

print("✅ access_token 获取成功")

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

    print(f"✅ 阿里云盘签到成功")
    print(f"📅 本月累计签到：{count} 天")
    print(f"🎁 今日奖励：{reward}")

else:
    print("❌ 签到失败")
    print(sign_result)
