import requests, json, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
TOKEN = "8782757289:AAF1J5w1i2bg0dBenGp2XZc3_yfqBPnXluU"
GROQ_API_KEY = ""
MEMOIRE_FILE = "memoire.json"
def load_memoire():
    if os.path.exists(MEMOIRE_FILE):
        return json.load(open(MEMOIRE_FILE))
    return {"nom": "GILDAS", "ville": "Lome", "messages": []}
def save_memoire(m):
    json.dump(m, open(MEMOIRE_FILE, "w"))
def agent_texte(prompt, memoire):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "openai/gpt-oss-20b", "max_tokens": 400, "temperature": 0.7, "messages": [{"role": "system", "content": f"Tu es SuperAgent, le bot de {memoire.get('nom','GILDAS')} a Lome. Tu n'es PAS ChatGPT, tu n'es PAS OpenAI. Tu parles TOUJOURS en francais simple, drole et utile."}, {"role": "user", "content": prompt}]}
    r = requests.post(url, headers=headers, json=data, timeout=30).json()
    return r["choices"][0]["message"]["content"] if "choices" in r else "Erreur Groq"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clavier = [[InlineKeyboardButton("Image", callback_data="image"), InlineKeyboardButton("Jeu", callback_data="jeu")], [InlineKeyboardButton("Meteo Lome", callback_data="meteo"), InlineKeyboardButton("Parler", callback_data="parler")]]
    await update.message.reply_text("SuperAgent v4 - Salut GILDAS ! Choisis :", reply_markup=InlineKeyboardMarkup(clavier))
async def boutons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    try:
        await q.answer()
    except:
        pass
    if q.data == "image":
        await q.message.reply_text("Envoie : /image un lion a Lome")
    elif q.data == "meteo":
        try:
            r = requests.get("https://wttr.in/Lome?format=j1", timeout=10).json()
            c = r['current_condition'][0]
            await q.message.reply_text(f"Lome: {c['weatherDesc'][0]['value']}, {c['temp_C']}C")
        except:
            await q.message.reply_text("Meteo indisponible")
    elif q.data == "jeu":
        await q.message.reply_text("Jeu : Je pense a un chiffre entre 1 et 10. Devine !")
    else:
        await q.message.reply_text("Parle-moi, je t'ecoute GILDAS !")
async def image_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Ex: /image une moto a Lome")
        return
    await update.message.reply_text("Je cree ton image...")
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    await update.message.reply_photo(photo=url, caption=f"Voila GILDAS : {prompt}")
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    memoire = load_memoire()
    memoire["messages"].append(txt)
    save_memoire(memoire)
    await update.message.reply_text("SuperAgent reflechit...")
    rep = agent_texte(txt, memoire)
    await update.message.reply_text(rep)
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("image", image_cmd))
app.add_handler(CallbackQueryHandler(boutons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
print("SuperAgent v4 lance...")
app.run_polling()
