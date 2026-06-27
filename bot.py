import os
import tempfile
import telebot
import yt_dlp
import threading

TOKEN = '8789963414:AAHSpfy-_wxi0hzsNtTY7WSKk_Dm7EeNgvM'
bot = telebot.TeleBot(TOKEN)

def download_music(query, tmpdir):
    sources = [
        {
            'default_search': 'scsearch1',
            'format': 'bestaudio[ext=mp3]/bestaudio',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        },
        {
            'default_search': 'ytsearch1',
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android']}},
        },
    ]
    for opts in sources:
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([query])
            files = [f for f in os.listdir(tmpdir) if not f.endswith('.part')]
            if files:
                return os.path.join(tmpdir, files[0])
        except:
            continue
    return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "🎵 *Prado Music Bot*\n\n"
        "Manda uma lista de músicas (uma por linha) e eu baixo os MP3s!\n\n"
        "Exemplo:\n"
        "Thiaguinho - Esquema Preferido\n"
        "Sorriso Maroto - Por Você\n"
        "Belo - Intriga da Oposição",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    lines = [l.strip() for l in message.text.split('\n') if l.strip()]
    if not lines:
        return
    if len(lines) > 15:
        bot.reply_to(message, "⚠️ Máximo 15 músicas por vez!")
        return

    def process():
        bot.reply_to(message, f"⏳ Processando {len(lines)} música(s)...")
        for i, music in enumerate(lines):
            msg = bot.send_message(message.chat.id, f"⬇️ {i+1}/{len(lines)}: *{music}*", parse_mode='Markdown')
            tmpdir = tempfile.mkdtemp()
            try:
                path = download_music(music, tmpdir)
                if path:
                    # Renomeia para .mp3 se necessário
                    if not path.endswith('.mp3'):
                        newpath = path.rsplit('.', 1)[0] + '.mp3'
                        os.rename(path, newpath)
                        path = newpath
                    with open(path, 'rb') as f:
                        bot.send_audio(message.chat.id, f, title=music)
                    bot.delete_message(message.chat.id, msg.message_id)
                else:
                    bot.edit_message_text(f"❌ Não encontrei: *{music}*", message.chat.id, msg.message_id, parse_mode='Markdown')
            except Exception as e:
                bot.edit_message_text(f"❌ Erro: *{music}*", message.chat.id, msg.message_id, parse_mode='Markdown')

    threading.Thread(target=process).start()

print("Bot iniciado!")
bot.infinity_polling()
