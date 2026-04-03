import os
import time
import random
import sqlite3
import logging
import asyncio
from datetime import datetime

# Third-party libraries
# pip install playwright python-telegram-bot ollama
from playwright.sync_api import sync_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import ollama

# --- CONFIGURATION ---
# Replace with your actual Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHROME_CDP_URL = "http://127.0.0.1:9222"
OLLAMA_MODEL = "qwen2.5:1.5b"
DB_NAME = "agent_memory.db"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- DATABASE / MEMORY SYSTEM ---
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

# --- AI GENERATION ---
def ai_generate_response(tweet_text):
    prompt = f"""
    You are a Web3-savvy, casual, and helpful social media assistant. 
    Generate a short, contextual reply to the following tweet.
    Use 1-2 relevant emojis. Keep it under 180 characters.
    
    Tweet: "{tweet_text}"
    
    Reply:
    """
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content'].strip().replace('"', '')
    except Exception as e:
        logger.error(f"Ollama Error: {e}")
        return "That's interesting! 🚀 #Web3"

# --- PLAYWRIGHT ACTIONS ---
def human_delay():
    time.sleep(random.uniform(1.5, 4.0))

def playwright_post_new(text):
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CHROME_CDP_URL)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            page.goto("https://x.com/compose/post")
            human_delay()
            
            # Use visual locators instead of CSS classes
            editor = page.get_by_role("textbox", name="Post text")
            editor.fill(text)
            human_delay()
            
            page.get_by_test_id("tweetButton").click()
            human_delay()
            return "✅ Post published successfully!"
        except Exception as e:
            return f"❌ Error posting: {str(e)}"

def playwright_reply_timeline(limit=3):
    results = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CHROME_CDP_URL)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            page.goto("https://x.com/home")
            human_delay()
            
            # Natural scrolling
            page.mouse.wheel(0, 500)
            human_delay()

            # Locate tweets using visual cues
            tweets = page.get_by_test_id("tweet").all()
            count = 0
            
            for tweet in tweets:
                if count >= limit: break
                
                try:
                    # Extract text content
                    tweet_text = tweet.get_by_test_id("tweetText").inner_text()
                    # Simple ID generation based on text hash for memory
                    tweet_id = str(hash(tweet_text))
                    
                    if is_tweet_processed(tweet_id):
                        continue
                    
                    # Generate AI Reply
                    reply_text = ai_generate_response(tweet_text)
                    
                    # Click Reply button
                    tweet.get_by_test_id("reply").click()
                    human_delay()
                    
                    # Fill and send
                    page.get_by_role("textbox", name="Post text").fill(reply_text)
                    human_delay()
                    page.get_by_test_id("tweetButtonInline").click()
                    
                    save_tweet_action(tweet_id, tweet_text, reply_text)
                    results.append(f"Replied to: {tweet_text[:30]}...")
                    count += 1
                    human_delay()
                    
                except Exception as inner_e:
                    logger.warning(f"Skipping tweet due to error: {inner_e}")
                    continue
                    
            return "\n".join(results) if results else "No new tweets to reply to."
        except Exception as e:
            return f"❌ Timeline Error: {str(e)}"

# --- TELEGRAM COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 X-Agent Command Center Active.\n\n"
        "Available Commands:\n"
        "/status - Check agent health\n"
        "/post_new <text> - Post a new tweet\n"
        "/reply_timeline - Auto-reply to latest tweets"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Agent is online and connected to local memory.")

async def post_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Please provide text: /post_new Hello World")
        return
    
    await update.message.reply_text("⏳ Connecting to Chrome and posting...")
    result = playwright_post_new(text)
    await update.message.reply_text(result)

async def reply_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Scanning timeline and generating AI replies...")
    result = playwright_reply_timeline()
    await update.message.reply_text(result)

# --- MAIN RUNNER ---
if __name__ == '__main__':
    init_db()
    
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("⚠️ ERROR: Please set your TELEGRAM_BOT_TOKEN in agent.py")
    else:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("post_new", post_new))
        app.add_handler(CommandHandler("reply_timeline", reply_timeline))
        
        print("🚀 Telegram Bot is running... Send commands to your bot!")
        app.run_polling()
