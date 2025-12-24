# Anki AI Dynamic Cards Add-on

Have you ever noticed how frustrating it is when learning a new word or phrase, you don't have access to an endless supply of real-life examples? This plugin solves that problem using AI! Each time, you will see new and relevant examples for the words and phrases you are studying. Currently, this plugin only supports English and simple cards either without formatting or with minimal formatting, where the word or phrase being studied is highlighted using `<b>` tags.

Anki AI Dynamic Cards is an add-on for Anki that dynamically generates example sentences related to words or phrases you are learning, using AI. This add-on provides a unique way to improve the effectiveness of memorizing new words and their usage in context, giving users the ability to practice real-world scenarios. These generated examples don't stored in database.

## Supported AI Providers

- **OpenAI** (GPT models)
- **Google Gemini**
- **Google Gemma** (Gemma models)
- **Anthropic** (Claude models)
- **Grok** (X.ai)
- **DeepSeek**
- **OpenRouter** (access to multiple models)

## Installation

From Anki app (Qt6):
- Tools -> Add-ons -> Get Add-ons... -> code [895469405](https://ankiweb.net/shared/info/895469405)
- Restart Anki
- Select your AI provider and enter API key in the dialog box when prompted

To install Anki AI Dynamic Cards manually, you need to download the add-on package from releases and install it manually. You can do this by following these steps:
- Download the add-on package from the [release page](https://github.com/AleksandrFurmenkovOfficial/anki-ai-dynamic-cards/releases/tag/v3)
- Find out an Anki add-ons directory. In Anki, select Tools > Add-ons > View Files. This will open the Anki add-ons directory
- Extract the downloaded package `anki-ai-dynamic-cards.zip` into the add-ons directory
- Restart Anki
- Select your AI provider and enter API key in the dialog box when prompted

To install the addon directly from the sources you need:
- Clone the repo
- Find out an Anki add-ons directory. In Anki, select Tools > Add-ons > View Files. This will open the Anki add-ons directory
- Restart Anki
- Select your AI provider and enter API key in the dialog box when prompted

## Configuration

You can configure the add-on in two ways:

1. **Settings Dialog**: Tools → AI Dynamic Cards Settings
2. **Standard Anki Config**: Tools → Add-ons → Select add-on → Config

Configuration options:
- `provider`: AI provider (`openai`, `google-gemini`, `google-gemma`, `anthropic`, `grok`, `deepseek`, `openrouter`)
- `api_key`: Your API key for the selected provider
- `model`: (optional) Specific model to use. If empty, uses default model for provider

## Building from Source

To build the `.ankiaddon` package from source code:

### Windows (PowerShell)
```powershell
Compress-Archive -Path '__init__.py', 'manifest.json', 'config.json' -DestinationPath 'ai-dynamic-cards.zip' -Force
Rename-Item 'ai-dynamic-cards.zip' 'ai-dynamic-cards.ankiaddon' -Force
```

### Linux / macOS
```bash
zip ai-dynamic-cards.ankiaddon __init__.py manifest.json config.json
```

### Required files for package:
- `__init__.py` - main addon code
- `manifest.json` - addon metadata
- `config.json` - default configuration

After building, install via: Tools → Add-ons → Install from file...

## Usage
To use Anki AI Dynamic Cards, you need to create a deck with cards that contains just a one word or phrase you want to memorize. Anki AI Dynamic Cards will automatically generate an example sentence for the word you are learning. You can then review the card as usual.
