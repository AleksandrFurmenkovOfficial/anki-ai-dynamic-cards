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

    <div id="example_container">Waiting for an update...</div>
    <div id="text_extracter" hidden></div>
    <div id="messages" hidden></div>
    <button id="regenExampleButton">Next example</button>

    <script>

    function extractText(html) {
        var container = document.getElementById('text_extracter');
        container.innerHTML = html;
        var text = container.textContent || container.innerText;
        document.getElementById('text_extracter').innerHTML = '';
        return text;
    }
    
    function getRandomTopics() {
        const topics = [
            "news", "politics", "science", "home", "work",
            "shop", "friends", "bank", "sports", "travel",
            "education", "health", "technology", "entertainment",
            "nature", "art", "cooking", "tv show", "AGI"
        ];
        let selectedTopics = [];
        
        while (selectedTopics.length < 3) {
            const randomIndex = Math.floor(Math.random() * topics.length);
            const topic = topics[randomIndex];
            if (!selectedTopics.includes(topic)) {
                selectedTopics.push(topic);
            }
        }
        
        return selectedTopics.join(", ");
    }

    function UpdateExample() {   
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
        }];

        document.getElementById('example_container').innerHTML = 'Waiting for an example...';

        let word = "";
        document.querySelectorAll('b').forEach(function(element) {
            word = element.textContent;
        });

        if (!word) {
            word = extractText('SOURCE_HTML');
        }

        card_messages.push(
        {
            "role": "user",
            "content": "Please give me another sentence for '" + word + "'. For the example use these topics " + getRandomTopics() 
        });
        
        fetch(`https://api.openai.com/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_ACTUAL_API_KEY_HERE'
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                temperature: 0.6,
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
    </script>
    """.replace("YOUR_ACTUAL_API_KEY_HERE", api_key).replace("SOURCE_HTML", remove_style_tags(html.replace('\n', '')))

gui_hooks.card_will_show.append(prepare)
