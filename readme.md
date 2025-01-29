# Telegram Vocabulary Practice Bot

![Bot Banner](https://imgur.com/your-banner-image.png) <!-- Replace with your bot's banner image URL -->

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
  - [Admin Functionalities](#admin-functionalities)
  - [User Functionalities](#user-functionalities)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Admin Usage](#admin-usage)
  - [User Usage](#user-usage)
  - [Canceling Operations](#canceling-operations)
- [Code Overview](#code-overview)
  - [`bot.py`](#botpy)
  - [`database.py`](#databasepy)
- [Database Schema](#database-schema)
- [Additional Recommendations](#additional-recommendations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Welcome to the **Telegram Vocabulary Practice Bot**! This bot is designed to help users practice vocabulary in both English and Uzbek. It offers functionalities for administrators to manage vocabulary subjects and words, as well as for regular users to engage in practice sessions with performance tracking.

## Features

### Admin Functionalities

- **Create Subjects:** Organize vocabulary into different subjects.
- **Delete Subjects:** Remove existing subjects and their associated words.
- **Add Words:** Add new vocabulary words with translations.
- **Delete Words:** Remove specific words from a subject.
- **Practice:** Admins can practice vocabulary to ensure accuracy and familiarity.

### User Functionalities

- **Choose Subject:** Select a subject to practice vocabulary.
- **Random Translation Direction:** Words are presented in either English or Uzbek randomly.
- **Performance Tracking:** Users receive a summary of correct and incorrect answers at the end of each session.
- **Interactive Feedback:** Immediate feedback on each translation attempt.

## Prerequisites

Before setting up the bot, ensure you have the following:

- **Python 3.7 or higher** installed on your system.
- A **Telegram Bot Token**. You can obtain one by talking to [@BotFather](https://t.me/BotFather) on Telegram.
- **Administrative Access:** Your Telegram user ID should be known to set up admin functionalities.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/My-name-is-Jamshidbek/dictionary_bot.git
   cd dictionary_bot
   ```

2. **Create a Virtual Environment:**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *If you don't have a `requirements.txt`, create one with the following content:*

   ```txt
   python-telegram-bot==20.3
   ```

   Then run:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

**Create a `config.py` File:**

   This file will store your bot's configuration details.

   ```python
   # config.py

   TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
   ADMIN_ID = YOUR_TELEGRAM_USER_ID  # Replace with your Telegram user ID (integer)
   DB_PATH = 'vocabulary.db'  # Path to your SQLite database file
   ```

   *Ensure that `config.py` is **excluded from version control** by adding it to your `.gitignore` to protect sensitive information.*

## Usage

### Admin Usage

Admins can perform the following operations:

- `/start` - Opens the admin panel.
- Select "Create Subject" to add a new vocabulary category.
- Select "Delete Subject" to remove an existing category.
- Select "Add Word" to add new words to a subject.
- Select "Delete Word" to remove a word from a subject.
- Select "Practice" to test vocabulary knowledge.

### User Usage

- `/start` - Opens the user panel.
- Select a subject to practice.
- The bot will randomly present words in either Uzbek or English.
- Users must input the correct translation.
- A summary is provided at the end of the session.

### Canceling Operations

Users can type `/cancel` at any time to return to the main menu.

## Code Overview

### `bot.py`

Handles the main bot functionality, including admin commands, user practice sessions, and message handling.

### `database.py`

Manages database interactions, including creating subjects, adding words, and fetching words for practice.

## Database Schema

The bot uses an SQLite database with the following structure:

- `subjects`
  - `id` (INTEGER, PRIMARY KEY)
  - `name` (TEXT, UNIQUE, NOT NULL)

- `words`
  - `id` (INTEGER, PRIMARY KEY)
  - `subject_id` (INTEGER, FOREIGN KEY)
  - `uzbek` (TEXT, NOT NULL)
  - `english` (TEXT, NOT NULL)

## Additional Recommendations

- Secure `config.py` by **excluding it from version control**.
- Consider **using Docker** for easier deployment.
- Test the bot using a **Telegram sandbox group** before deployment.

## Troubleshooting

- **Bot not responding?** Check if your token is correct.
- **Database issues?** Ensure the `vocabulary.db` file exists and has the correct schema.
- **Permission errors?** Run the bot with proper permissions: `python3 bot.py`.

## Contributing

Pull requests are welcome! Please ensure your code is well-documented.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

