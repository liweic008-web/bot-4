import os
from datetime import datetime
import discord
from discord.ext import commands
import pytz
import requests

# 🚨 貼上你想讓天氣機器人發言的 Discord 頻道 ID
CHANNEL_ID = 1527992244043255899  

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CWA_TOKEN = os.getenv("CWA_TOKEN")  # 氣象局授權碼

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_weather_report():
    if not CWA_TOKEN:
        return "⚠️ 【系統警告】未設定 CWA_TOKEN，無法獲取氣象資料。"
    
    try:
        # 抓取氣象局預報 API
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWA_TOKEN}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 預設地點（可自行更換，例如 "臺北市", "高雄市"）
        target_location = "臺中市"
        location_data = None
        
        for loc in data["records"]["location"]:
            if loc["locationName"] == target_location:
                location_data = loc
                break
                
        if not location_data:
            return f"❌ 找不到 {target_location} 的天氣資料。"
            
        weather_elements = location_data["weatherElement"]
        wx = weather_elements[0]["time"][0]["parameter"]["parameterName"]  # 天氣狀態
        pop = weather_elements[1]["time"][0]["parameter"]["parameterName"] # 降雨機率
        min_t = weather_elements[2]["time"][0]["parameter"]["parameterName"] # 最低溫
        max_t = weather_elements[4]["time"][0]["parameter"]["parameterName"] # 最高溫
        
        pop_int = int(pop) if pop.isdigit() else 0
        if pop_int >= 70:
            tips = "🚨 降雨機率極高！出門請務必攜帶折疊傘！"
        elif 30 <= pop_int < 70:
            tips = "⛅ 天氣不太穩定，建議帶傘備用。"
        else:
            tips = "☀️ 天氣晴朗或多雲，是個適合做研究的好日子！"
            
        tw_tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(tw_tz)

        # 組裝純天氣報告
        report = f"═══ 空間站每日氣象廣播 ═══\n"
        report += f"播報時間：{now.strftime('%m/%d %H:%M')}\n"
        report += f"觀測區域：{target_location}\n"
        report += f"天氣狀態：{wx}\n"
        report += f"氣溫預測：{min_t}°C ～ {max_t}°C\n"
        report += f"降雨機率：{pop}%\n"
        report += f"站長提醒：{tips}\n"
        report += f"═══════════════════════"
        return report

    except Exception as e:
        return f"❌ 抓取氣象失敗，錯誤訊息: {e}"

@bot.event
async def on_ready():
    print(f"【天氣機器人】{bot.user} 已上線。")
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"【錯誤】找不到頻道 ID：{CHANNEL_ID}")
        await bot.close()
        return

    # 抓取天氣報告並發送
    report = get_weather_report()
    await channel.send(report)
    print("【成功】天氣預報已發送，準備關機。")
    await bot.close()

bot.run(DISCORD_TOKEN)
