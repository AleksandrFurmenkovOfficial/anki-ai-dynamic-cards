import os
import sys
from typing import Tuple
from anki import hooks
from anki.template import TemplateRenderContext, TemplateRenderOutput
from aqt import mw
from PyQt5.QtWidgets import QInputDialog

addon_name = "anki-ai-dynamic-cards"
addon_path = os.path.join(mw.pm.addonFolder(), addon_name)
sys.path.append(addon_path)
import openai

is_api_key_valid = False

def on_card_did_render(output: TemplateRenderOutput, context: TemplateRenderContext):
    if not is_api_key_valid:
        return

    try:
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": "You are an english teacher. You should give 3 examples, each on a new line via <br> tag, for the word which user will provide. The source word should be bold via <b> tags."}, 
            {"role": "user", "content": output.question_text}])
        output.question_text = completion.choices[0].message.content
    except:
        pass

api_key_file = os.path.join(addon_path, "api_key.txt")
api_key = ""
try:
    with open(api_key_file, "r") as file:
        api_key = file.read()
except:
    pass

if api_key == "":
    try:
        api_key, ok = QInputDialog.getText(None, "Provide OpenAI api key", "OpenAI key:", text="sk-XXXXXXXXXXX")
        if ok:
            with open(api_key_file, "w") as file:
                file.write(api_key)
    except:
        pass

try:
    if api_key != "":
        openai.api_key = api_key
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "system", "content": "Hi!"}])
        is_api_key_valid = True
except:
    if (os.path.isfile(api_key_file)):
        os.remove(api_key_file)

hooks.card_did_render.append(on_card_did_render)
