import asyncio
from datetime import datetime
import logging
import sqlite3
import random

from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import ollama

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHROME_CDP_URL = "http://127.0.0.1:9222"
OLLAMA_MODEL = "qwen2.5:1.5b"
DB_NAME = "agent_memory.db"
AUTO_POST_RUNNING = False

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_tweets (
            tweet_id TEXT PRIMARY KEY,
            content TEXT,
            reply TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def is_tweet_processed(tweet_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_tweets WHERE tweet_id = ?', (tweet_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_tweet_action(tweet_id, content, reply):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO processed_tweets (tweet_id, content, reply, timestamp) VALUES (?, ?, ?, ?)',
        (tweet_id, content, reply, datetime.now())
    )
    conn.commit()
    conn.close()

def ai_generate_response(tweet_text):
    prompt = f"""
    You are a real human, casual Web3 user.
    Reply to this tweet naturally.
    RULES:
    1. STRICTLY NO HASHTAGS! Never use the '#' symbol.
    2. Keep it short, like a normal human comment (under 100 characters).
    3. Maximum 1 emoji. Don't be cringy or robotic.
    
    Tweet: "{tweet_text}"
    
    Reply:
    """
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'user', 'content': prompt},
        ])
        
        reply_raw = response['message']['content'].strip().replace('"', '')
        
        reply_clean = ' '.join(word for word in reply_raw.split() if not word.startswith('#'))
        return reply_clean
    except Exception as e:
        logger.error(f"Ollama Error: {e}")
        return "LFG! 🚀"

def ai_generate_tweet(prompt):
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'user', 'content': prompt},
        ])
        tweet_raw = response['message']['content'].strip().replace('"', '')
        
        tweet_clean = ' '.join(word for word in tweet_raw.split() if not word.startswith('#'))
        return tweet_clean
    except Exception as e:
        logger.error(f"Ollama Error generating tweet: {e}")
        return "Market is wild today! Stay safe out there. 🚀"

async def human_delay():
    await asyncio.sleep(random.uniform(1.5, 4.0))

async def cooldown_delay():
    waktu_tunggu = random.uniform(30.0, 40.0)
    print(f"⏳ Jeda santai manusia... Menunggu {waktu_tunggu:.1f} detik sebelum scroll ke tweet berikutnya.")
    await asyncio.sleep(waktu_tunggu)

async def playwright_post_new(text):
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto("https://x.com/compose/post")
            await human_delay()
            
            editor = page.get_by_role("textbox", name="Post text")
            await editor.fill(text)
            await human_delay()
            
            await page.get_by_test_id("tweetButton").click()
            await human_delay()
            return "✅ Post published successfully!"
        except Exception as e:
            return f"❌ Error posting: {str(e)}"

async def playwright_reply_timeline(limit=3):
    results = []
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            await page.goto("https://x.com/home")
            await human_delay()
            
            await page.mouse.wheel(0, 500)
            await human_delay()

            tweets = await page.get_by_test_id("tweet").all()
            count = 0
            
            for tweet in tweets:
                if count >= limit: break
                
                try:
                    tweet_text = await tweet.get_by_test_id("tweetText").inner_text()
                    tweet_id = str(hash(tweet_text))
                    
                    if is_tweet_processed(tweet_id):
                        continue
                    
                    reply_text = ai_generate_response(tweet_text)
                    
                    
                    await tweet.get_by_test_id("reply").click(force=True)
                    await human_delay()
                    
                    await page.keyboard.type(reply_text)
                    await human_delay()
                    
                    await page.keyboard.press("Control+Enter")
                    
                    
                    save_tweet_action(tweet_id, tweet_text, reply_text)
                    results.append(f"Replied to: {tweet_text[:30]}...")
                    count += 1
                    await human_delay()
                        
                    if count < limit:
                        await cooldown_delay()
                    
                except Exception as inner_e:
                    logger.warning(f"Skipping tweet due to error: {inner_e}")
                    continue
                    
            return "\n".join(results) if results else "No new tweets to reply to."
        except Exception as e:
            return f"❌ Timeline Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 X-Agent Command Center Active.\n\n"
        "Available Commands:\n"
        "/status - Check agent health\n"
        "/post_new <text> - Post a new tweet\n"
        "/reply_timeline - Auto-reply latest tweets\n"
        "/auto_post - Nyalakan patroli & posting otomatis\n"
        "/stop_autopost - Matikan mesin otonom"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Agent is online and connected to local memory.")

async def post_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please provide text: /post_new Hello World")
        return
    
    await update.message.reply_text("⏳ Connecting to Chrome and posting...")
    result = await playwright_post_new(text)
    await update.message.reply_text(result)

async def reply_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Scanning timeline and generating AI replies...")
    result = await playwright_reply_timeline()
    await update.message.reply_text(result)

async def scout_viral_topics():
    keywords = ["Web3 Alpha", "Crypto market", "AI", "Airdrop", "AI Automation", "OpenClaw", "ClaudeCode"]
    target = random.choice(keywords)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            
            search_url = f"https://x.com/search?q=({target}) min_faves:500&f=live"
            await page.goto(search_url)
            await asyncio.sleep(5) # Kasih waktu loading
            
            elements = await page.get_by_test_id("tweetText").all()
            raw_data = ""
            for el in elements[:3]:
                raw_data += await el.inner_text() + "\n---\n"
            
            return raw_data if raw_data else "No fresh data found."
        except Exception as e:
            logger.error(f"Scout Error: {e}")
            return "Market is moving fast."

async def autonomous_loop(context: ContextTypes.DEFAULT_TYPE, chat_id):
    global AUTO_POST_RUNNING
    while AUTO_POST_RUNNING:
        try:

            data_mentah = await scout_viral_topics()
            
            prompt = f"Based on this raw info: '{data_mentah}', create a smart, high-level Web3/Tech update tweet. No hashtags. Max 180 chars. Indonesia or English mix."
            tweet_text = ai_generate_tweet(prompt) 
            
            result = await playwright_post_new(tweet_text)
            
            await context.bot.send_message(chat_id=chat_id, text=f"🤖 [Auto-Post Berhasil]\n\nTopik: {tweet_text}\n\nStatus: {result}")
            
            jeda_menit = random.randint(60, 120)
            await asyncio.sleep(jeda_menit * 60)
            
        except Exception as e:
            logger.error(f"Loop Error: {e}")
            await asyncio.sleep(300)

async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_RUNNING
    if AUTO_POST_RUNNING:
        await update.message.reply_text("⚠️ Mesin sudah menyala, Bos!")
        return
    
    AUTO_POST_RUNNING = True
    await update.message.reply_text("🚀 Agen Intelijen Aktif! Saya akan patroli di X dan posting setiap 1-2 jam secara otomatis.")
    
    asyncio.create_task(autonomous_loop(context, update.effective_chat.id))

async def stop_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_POST_RUNNING
    AUTO_POST_RUNNING = False
    await update.message.reply_text("🛑 Mesin Otonom DIMATIKAN. Saya akan berhenti setelah tugas terakhir selesai.")

if __name__ == '__main__':
    init_db()
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("post_new", post_new))
    app.add_handler(CommandHandler("reply_timeline", reply_timeline))
    app.add_handler(CommandHandler("auto_post", start_auto))
    app.add_handler(CommandHandler("stop_autopost", stop_auto))
    
    print("🚀 Telegram Bot is running... Send commands to your bot!")
    app.run_polling()
