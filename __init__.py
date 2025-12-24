import os
import re
from aqt import mw, gui_hooks
from aqt.qt import QAction
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QFormLayout

# Provider configurations
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-5-nano"
    },
    "google-gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "default_model": "gemini-2.5-flash"
    },
    "google-gemma": {
        "name": "Google Gemma",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "default_model": "gemma-3-27b-it",
        "supports_system": False
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-haiku-4-5"
    },
    "grok": {
        "name": "Grok (X.ai)",
        "base_url": "https://api.x.ai/v1/chat/completions",
        "default_model": "grok-4-1-fast-non-reasoning"
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/chat/completions",
        "default_model": "deepseek-chat"
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "openai/gpt-5-nano"
    }
}


def get_config():
    """Get addon config using Anki's standard config mechanism."""
    config = mw.addonManager.getConfig(__name__) or {}
    return {
        "provider": config.get("provider", "openai"),
        "api_key": config.get("api_key", ""),
        "model": config.get("model", "")
    }


# Migrate from old api_key.txt if exists
def migrate_old_config():
    addon_path = os.path.dirname(__file__)
    old_api_key_file = os.path.join(addon_path, "api_key.txt")

    if os.path.exists(old_api_key_file):
        config = get_config()
        if not config.get("api_key"):
            try:
                with open(old_api_key_file, "r") as f:
                    old_key = f.read().strip()
                    if old_key:
                        config["api_key"] = old_key
                        config["provider"] = "openai"
                        mw.addonManager.writeConfig(__name__, config)
                        os.remove(old_api_key_file)
            except:
                pass

migrate_old_config()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Dynamic Cards Settings")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_current_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Provider selection
        self.provider_combo = QComboBox()
        for key, provider in PROVIDERS.items():
            self.provider_combo.addItem(provider["name"], key)
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        form_layout.addRow("Provider:", self.provider_combo)

        # API Key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("API Key:", self.api_key_input)

        # Model input
        self.model_input = QLineEdit()
        form_layout.addRow("Model (optional):", self.model_input)

        layout.addLayout(form_layout)

        # Hint label
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        # Info about standard config
        info_label = QLabel("You can also edit config via: Tools → Add-ons → Config")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_provider_changed(self):
        provider_key = self.provider_combo.currentData()
        provider = PROVIDERS[provider_key]
        self.model_input.setPlaceholderText(f"Default: {provider['default_model']}")
        self.hint_label.setText(f"Endpoint: {provider['base_url']}")

    def load_current_config(self):
        config = get_config()
        provider = config.get("provider", "openai")

        index = self.provider_combo.findData(provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        self.api_key_input.setText(config.get("api_key", ""))
        self.model_input.setText(config.get("model", ""))
        self.on_provider_changed()

    def save_settings(self):
        config = {
            "provider": self.provider_combo.currentData(),
            "api_key": self.api_key_input.text().strip(),
            "model": self.model_input.text().strip()
        }
        mw.addonManager.writeConfig(__name__, config)
        self.accept()


def open_settings():
    dialog = SettingsDialog(mw)
    dialog.exec()


# Add menu item for settings
action = QAction("AI Dynamic Cards Settings", mw)
action.triggered.connect(open_settings)
mw.form.menuTools.addAction(action)


# Show settings dialog if no API key configured
def check_api_key():
    config = get_config()
    if not config.get("api_key"):
        from aqt.utils import showInfo
        showInfo("AI Dynamic Cards: Please configure your API key.")
        open_settings()

gui_hooks.main_window_did_init.append(check_api_key)


def remove_style_tags(text):
    cleaned_text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
    return cleaned_text


def prepare(html, card, context):
    if context != "reviewQuestion":
        return html

    config = get_config()
    provider_key = config.get("provider", "openai")
    api_key = config.get("api_key", "")
    provider = PROVIDERS.get(provider_key, PROVIDERS["openai"])
    model = config.get("model") or provider["default_model"]
    base_url = provider["base_url"]
    supports_system = provider.get("supports_system", True)

    return """
    <style>.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
    }</style>

    <div id="example_container">Crafting the next example...</div>
    <div id="source_content" hidden>SOURCE_HTML</div>
    <button id="regenExampleButton">Next example</button>

    <script>
    (function () {
        const API_CONFIG = {
            apiKey: 'API_KEY_PLACEHOLDER',
            baseUrl: 'BASE_URL_PLACEHOLDER',
            model: 'MODEL_PLACEHOLDER',
            providerKey: 'PROVIDER_KEY_PLACEHOLDER',
            supportsSystem: SUPPORTS_SYSTEM_PLACEHOLDER
        };

        const AI_DYNAMIC_CARDS_STATE = (function () {
            if (!window.__aiDynamicCardsState) {
                window.__aiDynamicCardsState = {
                    requestSeq: 0,
                    activeRequest: 0
                };
            }
            return window.__aiDynamicCardsState;
        })();

        function extractText(element) {
            return element ? (element.textContent || element.innerText || '') : '';
        }

        function getCurrentWord(sourceDiv) {
            if (!sourceDiv) {
                return '';
            }
            const boldElement = sourceDiv.querySelector('b');
            if (boldElement) {
                return (boldElement.textContent || '').trim();
            }
            return extractText(sourceDiv).trim();
        }

        function getRandomTopics() {
            const topics = [
                "news", "politics", "science", "home", "work",
                "shop", "friends", "bank", "sports", "travel",
                "education", "health", "technology", "entertainment",
                "nature", "art", "cooking", "tv show", "AGI"
            ];
            const selectedTopics = [];

            while (selectedTopics.length < 3) {
                const randomIndex = Math.floor(Math.random() * topics.length);
                const topic = topics[randomIndex];
                if (!selectedTopics.includes(topic)) {
                    selectedTopics.push(topic);
                }
            }

            return selectedTopics.join(", ");
        }

        function wait(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        function escapeHtml(value) {
            return String(value).replace(/[&<>"']/g, function (char) {
                return ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                })[char];
            });
        }

        async function readResponseBodySafe(response) {
            try {
                return await response.json();
            } catch (_) {
                try {
                    return await response.text();
                } catch (_) {
                    return null;
                }
            }
        }

        function extractErrorMessage(errorBody) {
            if (errorBody == null) {
                return '';
            }
            if (typeof errorBody === 'string') {
                return errorBody;
            }
            if (typeof errorBody === 'object') {
                const err = errorBody.error;
                if (err) {
                    if (typeof err === 'string') {
                        return err;
                    }
                    if (typeof err === 'object' && err.message) {
                        return String(err.message);
                    }
                }
                if (errorBody.message) {
                    return String(errorBody.message);
                }
                try {
                    return JSON.stringify(errorBody);
                } catch (_) {
                    return String(errorBody);
                }
            }
            return String(errorBody);
        }

        function renderFinalError(exampleContainer, word, error) {
            const code = error && error.code !== undefined ? String(error.code) : 'unknown';
            const message = error && error.message ? String(error.message) : 'Unknown error';
            exampleContainer.innerHTML =
                '<b>' + escapeHtml(word) + '</b><br>' +
                'Error (' + escapeHtml(code) + '): ' + escapeHtml(message);
        }

        function buildHeaders(config) {
            const headers = {'Content-Type': 'application/json'};
            if (config.providerKey === 'anthropic') {
                headers['x-api-key'] = config.apiKey;
                headers['anthropic-version'] = '2023-06-01';
                headers['anthropic-dangerous-direct-browser-access'] = 'true';
            } else {
                headers['Authorization'] = 'Bearer ' + config.apiKey;
            }
            return headers;
        }

        function describeNetworkError(error, config) {
            const parts = [];
            if (error) {
                if (error.name) {
                    parts.push(error.name);
                }
                if (error.message && error.message !== error.name) {
                    parts.push(error.message);
                }
            }
            parts.push('provider=' + config.providerKey);
            parts.push('url=' + config.baseUrl);
            if (config.providerKey === 'anthropic') {
                parts.push('hint=direct browser access may be blocked; consider Python proxy');
            }
            return parts.filter(Boolean).join(' | ');
        }

        function buildRequestBody(config, messages, messagesPlain, systemPrompt) {
            if (config.providerKey === 'anthropic') {
                const body = {
                    model: config.model,
                    max_tokens: 256,
                    temperature: 1,
                    messages: messagesPlain
                };
                if (config.supportsSystem) {
                    body.system = systemPrompt;
                }
                return body;
            }
            return {
                model: config.model,
                temperature: 1,
                messages: messages
            };
        }

        function extractExampleText(data, providerKey) {
            if (providerKey === 'anthropic') {
                if (data && Array.isArray(data.content)) {
                    const parts = data.content
                        .filter(part => part && part.type === 'text' && typeof part.text === 'string')
                        .map(part => part.text);
                    if (parts.length > 0) {
                        return parts.join('').trim();
                    }
                }
                if (data && typeof data.content === 'string') {
                    return data.content.trim();
                }
            }
            if (data && data.choices && data.choices.length > 0 && data.choices[0].message) {
                return data.choices[0].message.content.trim();
            }
            return '';
        }

        async function UpdateExample() {
            const exampleContainer = document.getElementById('example_container');
            const sourceDiv = document.getElementById('source_content');
            if (!exampleContainer || !sourceDiv) {
                return;
            }

            const currentWord = getCurrentWord(sourceDiv);
            if (!currentWord) {
                exampleContainer.textContent = "Couldn't detect a word/phrase on this card.";
                return;
            }

            const requestId = ++AI_DYNAMIC_CARDS_STATE.requestSeq;
            AI_DYNAMIC_CARDS_STATE.activeRequest = requestId;

            const systemPrompt = "You are a language teacher. Please provide a meaningful example for a provided word or phrase. The source word or phrase should be bolded using <b> tags. Do not write anything else except the example.";

            const fewShotMessages = [
                {
                    "role": "user",
                    "content": "Please give me another sentence for the word or phrase 'to deter', use the same language."
                },
                {
                    "role": "assistant",
                    "content": "The bright lights outside the house helped <b>deter</b> burglars from attempting to break in."
                }
            ];

            const userMessage = "Please give me another sentence for '" + currentWord + "'. For the example use these topics " + getRandomTopics();

            const messagesPlain = [
                ...fewShotMessages,
                {"role": "user", "content": userMessage}
            ];
            const messagesWithSystem = [
                {"role": "system", "content": systemPrompt},
                ...messagesPlain
            ];
            const messagesWithoutSystem = [
                ...fewShotMessages,
                {"role": "user", "content": systemPrompt + "\\n\\n" + userMessage}
            ];
            const messages = API_CONFIG.supportsSystem ? messagesWithSystem : messagesWithoutSystem;

            const retryDelaysMs = [1000, 2000];
            let lastError = null;

            for (let attempt = 0; attempt < 1 + retryDelaysMs.length; attempt++) {
                if (!exampleContainer.isConnected || AI_DYNAMIC_CARDS_STATE.activeRequest !== requestId) {
                    return;
                }

                if (attempt === 0) {
                    exampleContainer.textContent = 'Generating the next example...';
                } else {
                    const waitMs = retryDelaysMs[attempt - 1];
                    const codeForStatus = lastError && lastError.code !== undefined ? String(lastError.code) : 'unknown';
                    exampleContainer.textContent = 'Error (' + codeForStatus + '). Retrying in ' + (waitMs / 1000) + 's...';
                    await wait(waitMs);
                    if (!exampleContainer.isConnected || AI_DYNAMIC_CARDS_STATE.activeRequest !== requestId) {
                        return;
                    }
                    exampleContainer.textContent = 'Generating the next example...';
                }

                try {
                    const response = await fetch(API_CONFIG.baseUrl, {
                        method: 'POST',
                        headers: buildHeaders(API_CONFIG),
                        body: JSON.stringify(buildRequestBody(API_CONFIG, messages, messagesPlain, systemPrompt))
                    });

                    if (!exampleContainer.isConnected || AI_DYNAMIC_CARDS_STATE.activeRequest !== requestId) {
                        return;
                    }

                    if (!response.ok) {
                        const errorBody = await readResponseBodySafe(response);
                        const message = extractErrorMessage(errorBody) || response.statusText || 'HTTP error';
                        lastError = {code: response.status, message: message};

                        if (attempt < retryDelaysMs.length) {
                            continue;
                        }

                        renderFinalError(exampleContainer, currentWord, lastError);
                        return;
                    }

                    let data = null;
                    try {
                        data = await response.json();
                    } catch (error) {
                        lastError = {code: 'parse_error', message: error && error.message ? error.message : String(error)};
                        if (attempt < retryDelaysMs.length) {
                            continue;
                        }
                        renderFinalError(exampleContainer, currentWord, lastError);
                        return;
                    }

                    if (!exampleContainer.isConnected || AI_DYNAMIC_CARDS_STATE.activeRequest !== requestId) {
                        return;
                    }

                    const exampleText = extractExampleText(data, API_CONFIG.providerKey);
                    if (exampleText) {
                        let example = exampleText;
                        example = example.replace(/\\*\\*(.+?)\\*\\*/g, '<b>$1</b>');
                        exampleContainer.innerHTML = example;
                        return;
                    }

                    lastError = {code: 'invalid_response', message: 'No completion found or error in response data.'};
                    if (attempt < retryDelaysMs.length) {
                        continue;
                    }

                    renderFinalError(exampleContainer, currentWord, lastError);
                    return;
                } catch (error) {
                    if (!exampleContainer.isConnected || AI_DYNAMIC_CARDS_STATE.activeRequest !== requestId) {
                        return;
                    }

                    lastError = {code: 'network_error', message: describeNetworkError(error, API_CONFIG)};
                    if (attempt < retryDelaysMs.length) {
                        continue;
                    }

                    renderFinalError(exampleContainer, currentWord, lastError);
                    return;
                }
            }
        }

        function setupDynamicCards() {
            const exampleContainer = document.getElementById('example_container');
            const sourceDiv = document.getElementById('source_content');
            if (!exampleContainer || !sourceDiv) {
                return;
            }

            const regenButton = document.getElementById('regenExampleButton');
            if (regenButton) {
                regenButton.onclick = UpdateExample;
            }

            if (exampleContainer.dataset.aiDynamicCardsInitialized !== '1') {
                exampleContainer.dataset.aiDynamicCardsInitialized = '1';
                UpdateExample();
            }
        }

        setupDynamicCards.__aiDynamicCards = true;

        if (typeof onUpdateHook !== 'undefined') {
            const alreadyRegistered = onUpdateHook.some(fn => fn && fn.__aiDynamicCards);
            if (!alreadyRegistered) {
                onUpdateHook.push(setupDynamicCards);
            }
        }

        // Run once in case scripts are executed after the DOM update hooks.
        setupDynamicCards();
    })();
    </script>
    """.replace("API_KEY_PLACEHOLDER", api_key).replace("BASE_URL_PLACEHOLDER", base_url).replace("MODEL_PLACEHOLDER", model).replace("PROVIDER_KEY_PLACEHOLDER", provider_key).replace("SUPPORTS_SYSTEM_PLACEHOLDER", str(supports_system).lower()).replace("SOURCE_HTML", remove_style_tags(html.replace('\n', '')))

gui_hooks.card_will_show.append(prepare)
