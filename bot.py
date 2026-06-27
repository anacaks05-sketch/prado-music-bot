import os
import tempfile
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.environ.get('BOT_TOKEN', '8789963414:AAHSpfy-_wxi0hzsNtTY7WSKk_Dm7EeNgvM')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 *Prado Music Bot*\n\n"
        "Manda uma lista de músicas (uma por linha) e eu baixo os MP3s pra você!\n\n"
        "Exemplo:\n"
        "Thiaguinho - Esquema Preferido\n"
        "Sorriso Maroto - Por Você\n"
        "Belo - Intriga da Oposição",
        parse_mode='Markdown'
    )

async def download_music(query):
    tmpdir = tempfile.mkdtemp()
    
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
            files = os.listdir(tmpdir)
            if files:
                return os.path.join(tmpdir, files[0])
        except:
            continue
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    if not lines:
        return
    
    if len(lines) > 15:
        await update.message.reply_text("⚠️ Máximo 15 músicas por vez!")
        return

    await update.message.reply_text(f"⏳ Processando {len(lines)} música(s)... aguarda!")

    for i, music in enumerate(lines):
        status_msg = await update.message.reply_text(f"⬇️ Baixando {i+1}/{len(lines)}: *{music}*", parse_mode='Markdown')
        
        try:
            path = await asyncio.get_event_loop().run_in_executor(None, lambda m=music: asyncio.run(download_music_sync(m)))
            
            if path and os.path.exists(path):
                fname = os.path.basename(path)
                # Garante extensão mp3
                if not fname.endswith('.mp3'):
                    newpath = path.rsplit('.', 1)[0] + '.mp3'
                    os.rename(path, newpath)
                    path = newpath
                    fname = os.path.basename(path)

                with open(path, 'rb') as f:
                    await update.message.reply_audio(
                        audio=f,
                        title=music,
                        filename=fname
                    )
                await status_msg.delete()
            else:
                await status_msg.edit_text(f"❌ Não encontrei: *{music}*", parse_mode='Markdown')
        except Exception as e:
            await status_msg.edit_text(f"❌ Erro em *{music}*: {str(e)[:100]}", parse_mode='Markdown')

    await update.message.reply_text("✅ Concluído!")

def download_music_sync(query):
    tmpdir = tempfile.mkdtemp()
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
            files = os.listdir(tmpdir)
            if files:
                return os.path.join(tmpdir, files[0])
        except:
            continue
    return None

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
