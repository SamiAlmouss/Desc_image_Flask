import asyncio
import os
import threading

from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler, ContextTypes,filters
from google import genai
from google.genai import types
from telegram.constants import ParseMode
client = genai.Client(api_key='AIzaSyBx-_j1iByYESGScCjHQ4EaHWlBaFwJmQA')
TOKEN = '7763059278:AAGOq5p41F62XU0DTwoeNKa4HBtHEDRr8j4'
tasks = []

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Welcome to Telegram bot for describing images!</p>"

def run_app():
    app.run(port=7999,host='0.0.0.0')

t = threading.Thread(target=run_app, args = ())
t.start()



class Prompt:
    update: Update
    context: ContextTypes.DEFAULT_TYPE
    def __init__(self,update, context, photo_name):
        self.photo_name = photo_name
        self.update = update
        self.context = context

process_fertig = False

def desc(photo_name) -> str:
    global process_fertig
    process_fertig = False
    with open(f'./temp/{photo_name}', 'rb') as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            'Describe the image using ten simple and easy Arabic sentences, then translate these sentences into German (at A2 level, as in a German language exam) without using English. Arrange the sentences so that each German sentence appears directly below its corresponding Arabic sentence. Format the result so that it can be displayed as a message on the Telegram app in a neat and attractive way. without markdown code'
        ]
    )
    os.remove(f'./temp/{photo_name}')
    process_fertig = True
    return response.text



async def help_func(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage(chat_id=update.effective_chat.id,
                                  text="To describe an image using ten sentences in Arabic and German, please send the image.\n\nUm eine Bildbeschreibung mit zehn Sätzen auf Arabisch und Deutsch zu erstellen, senden Sie bitte das Bild.\n\n من اجل وصف صورة بعشر جمل باللغة العربية والالمانية، من فضلك ارسل الصورة")

async def start_func(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await context.bot.sendMessage(chat_id=update.effective_chat.id,text="To describe an image using ten sentences in Arabic and German, please send the image.\n\nUm eine Bildbeschreibung mit zehn Sätzen auf Arabisch und Deutsch zu erstellen, senden Sie bitte das Bild.\n\n من اجل وصف صورة بعشر جمل باللغة العربية والالمانية، من فضلك ارسل الصورة")


async def pick_task(prompt:Prompt):
    await prompt.context.bot.sendMessage(chat_id=prompt.update.effective_chat.id, text='جاري تحليل الصورة . الرجاء الانتظار...')
    desc_image = desc(prompt.photo_name)
    loop5 = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(qus_send(desc_image, prompt.update, prompt.context), loop5)


async  def msg_func(update: Update,context: ContextTypes.DEFAULT_TYPE):
    photo_name=''
    file_id=''
    if filters.PHOTO.check_update(update):
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f'{unique_file_id}.jpg'

    elif filters.Document.IMAGE:
        file_id = update.message.document.file_id
        _,f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        photo_name = f'{unique_file_id}.{f_ext}'

    photo_file = await context.bot.getFile(file_id)
    await photo_file.download_to_drive(custom_path=f'./temp/{photo_name}')
    await pick_task(Prompt(update,context,photo_name))

async def qus_send(txt,update: Update,context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=txt,parse_mode=ParseMode.MARKDOWN)
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    help_handler = CommandHandler('help',  help_func)
    start_handler = CommandHandler('start', start_func)
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, msg_func)

    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    print("Your Bot Is Started ...")
    application.run_polling()

if __name__=="__main__":
    main()





