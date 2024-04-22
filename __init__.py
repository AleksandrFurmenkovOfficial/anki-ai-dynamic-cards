import os
import re
from aqt import mw, gui_hooks
from PyQt6.QtWidgets import QInputDialog

addon_name = "895469405"
addon_path = os.path.join(mw.pm.addonFolder(), addon_name)
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

def remove_style_tags(text):
    cleaned_text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
    return cleaned_text

def prepare(html, card, context):
    if context != "reviewQuestion":
        return html

    return """
    <style>.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
    }</style>

    <div id='example_container'>Waiting for an update...</div>
    <div id="text_extracter"></div>
    <button id="regenExampleButton">Next example</button>

    <script>
    function extractText() {
        var container = document.getElementById('text_extracter');
        var text = container.textContent || container.innerText;
        return text;
    }

    let card_messages = [
        {
            "role": "system",
            "content": "You are an language teacher. Please provide a meaningful example for a provided word or phrase. The source word or phrase should be bolded using <b> tags. Do not write anything else except the example."
        }, {
            "role": "user",
            "content": "Please give me another sentence for the word or phrase 'to deter', use the same language." 
        }, {
            "role": "assistant",
            "content": "The bright lights outside the house helped <b>deter</b> burglars from attempting to break in." 
        } 
    ];

    function UpdateExample() {
        document.getElementById('example_container').innerHTML = 'Waiting for an example...';

        let word = "";

        var boldElements = document.querySelectorAll('b');
        boldElements.forEach(function(element) {
            word = element.textContent;
        });

        if (!word) {
            document.getElementById('text_extracter').innerHTML = 'SOURCE_HTML';
            word = extractText();
            document.getElementById('text_extracter').innerHTML = '';
        }

        if (!word) {
            word = `SOURCE_HTML`;
        }

        card_messages.push(
        {
           "role": "user",
            "content": "Please give me another sentence for the word or phrase '" + word + "', use the same language." 
        });
        
        fetch(`https://api.openai.com/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_ACTUAL_API_KEY_HERE'
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                temperature: 0.66,
                messages: card_messages
            })
        })
        .then(response => {
            if (response.ok) {
                document.getElementById('example_container').innerHTML = 'API request successful. Parsing data...';
                return response.json();
            } else {
                return response.json().then(errorContent => {
                    document.getElementById('example_container').innerHTML = 'Error with API request. Status: ' + response.status + ' Error content: ' + JSON.stringify(errorContent);
                });
            }
        })
        .then(data => {
            if (data.choices && data.choices.length > 0) {
                const example = data.choices[0].message.content.trim();
                card_messages.push(
                {
                   "role": "assistant",
                    "content": example 
                });

                document.getElementById('example_container').innerHTML = example;
            } else {
                document.getElementById('example_container').innerHTML = 'No completion found or error in response data.';
            }
        })
        .catch(error => {
            document.getElementById('example_container').innerHTML = 'Error: ' + error.message;
        });
    }

    onUpdateHook.push(UpdateExample);
    regenExampleButton.addEventListener("click", UpdateExample);

    </script>""".replace("YOUR_ACTUAL_API_KEY_HERE", api_key).replace("SOURCE_HTML", remove_style_tags(html.replace('\n', '')))

gui_hooks.card_will_show.append(prepare)
