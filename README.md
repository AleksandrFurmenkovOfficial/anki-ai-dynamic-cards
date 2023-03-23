# Anki AI Dynamic Cards Add-on
Anki AI Dynamic Cards is an add-on for Anki that dynamically generates example sentences related to the words you are learning, using the artificial intelligence tool ChatGPT. This add-on provides a unique way to improve the effectiveness of memorizing new words and their usage in context, giving users the ability to practice real-world scenarios.

## Installation
To install Anki AI Dynamic Cards, you need to download the add-on package `anki-ai-dynamic-cards.zip` and install it manually. You can do this by following these steps:
- Download the add-on package from the [release page](https://github.com/AleksandrFurmenkovOfficial/anki-ai-dynamic-cards/releases/tag/v1)
- Find out an Anki add-ons directory. In Anki, select Tools > Add-ons > View Files. This will open the Anki add-ons directory
- Extract the downloaded package `anki-ai-dynamic-cards.zip` into the add-ons directory
- Restart Anki

To install the addon directly from the sources you need:
- Clone the repo
- Find out an Anki add-ons directory. In Anki, select Tools > Add-ons > View Files. This will open the Anki add-ons directory
- `pip install -r openai -t ANKI_ADDONS_DIRECTORY`
- Restart Anki

## Usage
To use Anki AI Dynamic Cards, you need to create a deck with cards that contains just a one word you want to memorize. Anki AI Dynamic Cards will automatically generate an example sentence for the word you are learning, using ChatGPT. You can then review the card as usual.
