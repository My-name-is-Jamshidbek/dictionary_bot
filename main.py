# bot.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)
import logging
from config import ADMIN_ID, TOKEN, DB_PATH
from database import Database
import random  # To randomize translation direction

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Database
db = Database(DB_PATH)

# Define states for ConversationHandler
(
    ADMIN_MENU,
    CREATE_SUBJECT,
    DELETE_SUBJECT,
    ADD_WORD_SELECT_SUBJECT,
    ADD_WORD_UZBEK,
    ADD_WORD_ENGLISH,
    DELETE_WORD_SELECT_SUBJECT,
    DELETE_WORD_SELECT_WORD,
    PRACTICE_SELECT_SUBJECT,    # New State for Practice
    PRACTICE_COMMUNICATE,       # New State for Practice Communication
    USER_SELECT_SUBJECT,
    USER_COMMUNICATE
) = range(12)

# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
            [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
            [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
            [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
            [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]  # New Practice Button
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADMIN_MENU
    else:
        # User menu
        subjects = db.get_subjects()
        if not subjects:
            await update.message.reply_text("❌ No subjects available. Please contact the admin.")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'user_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📚 *Choose a Subject to Practice:*', parse_mode='Markdown', reply_markup=reply_markup)
        return USER_SELECT_SUBJECT

# Admin Menu Callback Handler
async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'create_subject':
        await query.message.reply_text("✏️ *Enter the name of the new subject:*", parse_mode='Markdown')
        return CREATE_SUBJECT
    elif data == 'delete_subject':
        subjects = db.get_subjects()
        if not subjects:
            await query.message.reply_text("❌ No subjects to delete.")
            return ADMIN_MENU
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'delete_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('🗑️ *Select a Subject to Delete:*', parse_mode='Markdown', reply_markup=reply_markup)
        return DELETE_SUBJECT
    elif data == 'add_word':
        subjects = db.get_subjects()
        if not subjects:
            await query.message.reply_text("❌ No subjects available. Please create a subject first.")
            return ADMIN_MENU
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'add_word_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('➕ *Select a Subject to Add a Word:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADD_WORD_SELECT_SUBJECT
    elif data == 'delete_word':
        subjects = db.get_subjects()
        if not subjects:
            await query.message.reply_text("❌ No subjects available.")
            return ADMIN_MENU
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'delete_word_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('🗑️ *Select a Subject to Delete a Word:*', parse_mode='Markdown', reply_markup=reply_markup)
        return DELETE_WORD_SELECT_SUBJECT
    elif data == 'practice':  # Handle Practice Selection
        subjects = db.get_subjects()
        if not subjects:
            await query.message.reply_text("❌ No subjects available for practice.")
            return ADMIN_MENU
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'practice_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('🧑‍🏫 *Select a Subject to Practice:*', parse_mode='Markdown', reply_markup=reply_markup)
        return PRACTICE_SELECT_SUBJECT
    else:
        await query.message.reply_text("⚠️ *Unknown action.*", parse_mode='Markdown')
        return ADMIN_MENU

# Create Subject Handler
async def create_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject_name = update.message.text.strip()
    if not subject_name:
        await update.message.reply_text("❌ Subject name cannot be empty. Please enter a valid name:")
        return CREATE_SUBJECT
    success = db.create_subject(subject_name)
    if success:
        await update.message.reply_text(f"✅ *Subject '{subject_name}' created successfully.*", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"⚠️ *Subject '{subject_name}' already exists.*", parse_mode='Markdown')
    # Return to Admin Menu
    keyboard = [
        [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
        [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
        [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
        [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
        [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
    return ADMIN_MENU

# Delete Subject Callback Handler
async def delete_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: delete_subject_<subject>
    if not data.startswith('delete_subject_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ADMIN_MENU
    subject = data.split('delete_subject_')[1]
    success = db.delete_subject(subject)
    if success:
        await query.message.reply_text(f"✅ *Subject '{subject}' deleted successfully.*", parse_mode='Markdown')
    else:
        await query.message.reply_text(f"❌ *Failed to delete subject '{subject}'.*", parse_mode='Markdown')
    # Return to Admin Menu
    keyboard = [
        [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
        [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
        [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
        [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
        [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
    return ADMIN_MENU

# Add Word - Select Subject Callback Handler
async def add_word_select_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: add_word_subject_<subject>
    if not data.startswith('add_word_subject_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ADMIN_MENU
    subject = data.split('add_word_subject_')[1]
    context.user_data['add_word_subject'] = subject
    await query.message.reply_text(f"➕ *Adding a word to '{subject}':*\n\n✏️ *Step 1:* Enter the Uzbek word.", parse_mode='Markdown')
    return ADD_WORD_UZBEK

# Add Word - Receive Uzbek Word
async def add_word_receive_uzbek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uzbek_word = update.message.text.strip()
    if not uzbek_word:
        await update.message.reply_text("❌ Uzbek word cannot be empty. Please enter a valid word:")
        return ADD_WORD_UZBEK
    context.user_data['new_word_uzbek'] = uzbek_word
    await update.message.reply_text("✏️ *Step 2:* Enter the English translation.", parse_mode='Markdown')
    return ADD_WORD_ENGLISH

# Add Word - Receive English Word and Save
async def add_word_receive_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    english_word = update.message.text.strip()
    if not english_word:
        await update.message.reply_text("❌ English translation cannot be empty. Please enter a valid translation:")
        return ADD_WORD_ENGLISH
    subject = context.user_data.get('add_word_subject')
    uzbek_word = context.user_data.get('new_word_uzbek')
    success = db.add_word(subject, uzbek_word, english_word)
    if success:
        await update.message.reply_text(f"✅ *Word '{uzbek_word}' - '{english_word}' added to '{subject}'.*", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ *Failed to add word. Please try again.*", parse_mode='Markdown')
    # Return to Admin Menu
    keyboard = [
        [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
        [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
        [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
        [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
        [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
    return ADMIN_MENU

# Delete Word - Select Subject Callback Handler
async def delete_word_select_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: delete_word_subject_<subject>
    if not data.startswith('delete_word_subject_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ADMIN_MENU
    subject = data.split('delete_word_subject_')[1]
    words = db.get_words_by_subject(subject)
    if not words:
        await query.message.reply_text(f"❌ No words found in subject '{subject}'.")
        # Return to Admin Menu
        keyboard = [
            [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
            [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
            [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
            [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
            [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADMIN_MENU
    # Create buttons for each word
    keyboard = [
        [InlineKeyboardButton(f"{word[0]}: {word[1]} - {word[2]}", callback_data=f'delete_word_{word[0]}')]
        for word in words
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('🗑️ *Select a Word to Delete:*', parse_mode='Markdown', reply_markup=reply_markup)
    context.user_data['delete_word_subject'] = subject
    return DELETE_WORD_SELECT_WORD

# Delete Word - Confirm Deletion Callback Handler
async def delete_word_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: delete_word_<word_id>

    # Debugging: Log the received callback_data
    logger.info(f"Received callback_data in delete_word_confirm: {data}")

    if not data.startswith('delete_word_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ADMIN_MENU

    try:
        word_id_str = data.split('delete_word_')[1]
        word_id = int(word_id_str)
    except (IndexError, ValueError) as e:
        logger.error(f"Error parsing word_id from callback_data '{data}': {e}")
        await query.message.reply_text("❌ *Invalid word ID received.*", parse_mode='Markdown')
        return ADMIN_MENU

    subject = context.user_data.get('delete_word_subject')
    if not subject:
        logger.error("Subject not found in user_data during delete_word_confirm.")
        await query.message.reply_text("❌ *Subject information missing. Please try again.*", parse_mode='Markdown')
        return ADMIN_MENU

    success = db.delete_word(subject, word_id)
    if success:
        await query.message.reply_text("✅ *Word deleted successfully.*", parse_mode='Markdown')
    else:
        await query.message.reply_text("❌ *Failed to delete word.*", parse_mode='Markdown')
    # Return to Admin Menu
    keyboard = [
        [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
        [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
        [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
        [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
        [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
    return ADMIN_MENU

# Practice - Select Subject Callback Handler
async def practice_select_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: practice_subject_<subject>
    if not data.startswith('practice_subject_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ADMIN_MENU
    subject = data.split('practice_subject_')[1]
    words = db.get_words_by_subject(subject)
    if not words:
        await query.message.reply_text(f"❌ No words found in subject '{subject}'.")
        return ADMIN_MENU
    context.user_data['practice_subject'] = subject
    context.user_data['practice_words'] = words.copy()
    context.user_data['current_practice_index'] = 0
    # Initialize performance tracking
    context.user_data['practice_correct_answers'] = 0
    context.user_data['practice_incorrect_answers'] = 0
    # Send the first word with random direction
    current_word = words[0]
    translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
    context.user_data['practice_translation_direction'] = translation_direction  # Store direction for evaluation
    if translation_direction == 'uzbek_to_english':
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"
    await query.message.reply_text(prompt, parse_mode='Markdown')
    return PRACTICE_COMMUNICATE

# Practice - Receive Answer
async def practice_communicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().lower()
    words = context.user_data.get('practice_words')
    index = context.user_data.get('current_practice_index')
    translation_direction = context.user_data.get('practice_translation_direction')

    if index >= len(words):
        # This should not happen, but handle it gracefully
        await update.message.reply_text("🎉 *You've already completed all words in this subject.*", parse_mode='Markdown')
        return ConversationHandler.END

    current_word = words[index]

    if translation_direction == 'uzbek_to_english':
        correct_answer = current_word[2].lower()
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        correct_answer = current_word[1].lower()
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"

    if user_answer == correct_answer:
        context.user_data['practice_correct_answers'] += 1
        await update.message.reply_text("✅ *Correct!* 🎉", parse_mode='Markdown')
    else:
        context.user_data['practice_incorrect_answers'] += 1
        await update.message.reply_text(f"❌ *Incorrect.* The correct answer is: `{correct_answer}`", parse_mode='Markdown')

    # Move to next word
    context.user_data['current_practice_index'] += 1
    index += 1

    if index < len(words):
        next_word = words[index]
        # Randomize translation direction for the next word
        translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
        context.user_data['practice_translation_direction'] = translation_direction  # Update direction
        if translation_direction == 'uzbek_to_english':
            prompt = f"📝 *Translate to English:* {next_word[1]}"
        else:
            prompt = f"📝 *Translate to Uzbek:* {next_word[2]}"
        await update.message.reply_text(prompt, parse_mode='Markdown')
        return PRACTICE_COMMUNICATE
    else:
        # User has completed all words, show summary
        correct = context.user_data.get('practice_correct_answers', 0)
        incorrect = context.user_data.get('practice_incorrect_answers', 0)
        total = correct + incorrect

        # Calculate percentage
        if total > 0:
            percentage = (correct / total) * 100
        else:
            percentage = 0

        # Generate feedback based on performance
        if percentage == 100:
            feedback = "🎯 *Excellent!* You got all answers correct!"
        elif percentage >= 80:
            feedback = "👍 *Great job!* You scored highly."
        elif percentage >= 50:
            feedback = "🙂 *Good effort!* Keep practicing to improve."
        else:
            feedback = "🧐 *Needs Improvement.* Don't give up and keep learning!"

        summary = (
            f"🎉 *Practice Session Completed!*\n\n"
            f"✅ *Correct Answers:* {correct}\n"
            f"❌ *Incorrect Answers:* {incorrect}\n"
            f"📊 *Score:* {percentage:.2f}%\n\n"
            f"{feedback}"
        )

        await update.message.reply_text(summary, parse_mode='Markdown')

        # Return to Admin Menu
        keyboard = [
            [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
            [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
            [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
            [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
            [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADMIN_MENU

# User - Select Subject Callback Handler
async def user_select_subject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(1)
    query = update.callback_query
    await query.answer()
    data = query.data  # format: user_subject_<subject>
    if not data.startswith('user_subject_'):
        logger.warning(f"Unexpected callback_data format: {data}")
        await query.message.reply_text("⚠️ *Invalid data received.*", parse_mode='Markdown')
        return ConversationHandler.END
    subject = data.split('user_subject_')[1]
    words = db.get_words_by_subject(subject)
    if not words:
        await query.message.reply_text(f"❌ No words found in subject '{subject}'.")
        return ConversationHandler.END
    context.user_data['user_subject'] = subject
    context.user_data['user_words'] = words.copy()
    context.user_data['current_word_index'] = 0
    # Initialize performance tracking
    context.user_data['correct_answers'] = 0
    context.user_data['incorrect_answers'] = 0
    # Send the first word with random direction
    current_word = words[0]
    translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
    context.user_data['translation_direction'] = translation_direction  # Store direction for evaluation
    if translation_direction == 'uzbek_to_english':
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"
    await query.message.reply_text(prompt, parse_mode='Markdown')
    return USER_COMMUNICATE

# User Communication - Receive Answer
async def user_communicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().lower()
    words = context.user_data.get('user_words')
    index = context.user_data.get('current_word_index')
    translation_direction = context.user_data.get('translation_direction')

    if index >= len(words):
        # This should not happen, but handle it gracefully
        await update.message.reply_text("🎉 *You've already completed all words in this subject.*", parse_mode='Markdown')
        return ConversationHandler.END

    current_word = words[index]

    if translation_direction == 'uzbek_to_english':
        correct_answer = current_word[2].lower()
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        correct_answer = current_word[1].lower()
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"

    if user_answer == correct_answer:
        context.user_data['correct_answers'] += 1
        await update.message.reply_text("✅ *Correct!* 🎉", parse_mode='Markdown')
    else:
        context.user_data['incorrect_answers'] += 1
        await update.message.reply_text(f"❌ *Incorrect.* The correct answer is: `{correct_answer}`", parse_mode='Markdown')

    # Move to next word
    context.user_data['current_word_index'] += 1
    index += 1

    if index < len(words):
        next_word = words[index]
        # Randomize translation direction for the next word
        translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
        context.user_data['translation_direction'] = translation_direction  # Update direction
        if translation_direction == 'uzbek_to_english':
            prompt = f"📝 *Translate to English:* {next_word[1]}"
        else:
            prompt = f"📝 *Translate to Uzbek:* {next_word[2]}"
        await update.message.reply_text(prompt, parse_mode='Markdown')
        return USER_COMMUNICATE
    else:
        # User has completed all words, show summary
        correct = context.user_data.get('correct_answers', 0)
        incorrect = context.user_data.get('incorrect_answers', 0)
        total = correct + incorrect

        # Calculate percentage
        if total > 0:
            percentage = (correct / total) * 100
        else:
            percentage = 0

        # Generate feedback based on performance
        if percentage == 100:
            feedback = "🎯 *Excellent!* You got all answers correct!"
        elif percentage >= 80:
            feedback = "👍 *Great job!* You scored highly."
        elif percentage >= 50:
            feedback = "🙂 *Good effort!* Keep practicing to improve."
        else:
            feedback = "🧐 *Needs Improvement.* Don't give up and keep learning!"

        summary = (
            f"🎉 *Session Completed!*\n\n"
            f"✅ *Correct Answers:* {correct}\n"
            f"❌ *Incorrect Answers:* {incorrect}\n"
            f"📊 *Score:* {percentage:.2f}%\n\n"
            f"{feedback}"
        )

        await update.message.reply_text(summary, parse_mode='Markdown')

        return ConversationHandler.END

# Practice - Communicate Handler (Admin)
async def practice_communicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().lower()
    words = context.user_data.get('practice_words')
    index = context.user_data.get('current_practice_index')
    translation_direction = context.user_data.get('practice_translation_direction')

    if index >= len(words):
        # This should not happen, but handle it gracefully
        await update.message.reply_text("🎉 *You've already completed all words in this subject.*", parse_mode='Markdown')
        return ConversationHandler.END

    current_word = words[index]

    if translation_direction == 'uzbek_to_english':
        correct_answer = current_word[2].lower()
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        correct_answer = current_word[1].lower()
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"

    if user_answer == correct_answer:
        context.user_data['practice_correct_answers'] += 1
        await update.message.reply_text("✅ *Correct!* 🎉", parse_mode='Markdown')
    else:
        context.user_data['practice_incorrect_answers'] += 1
        await update.message.reply_text(f"❌ *Incorrect.* The correct answer is: `{correct_answer}`", parse_mode='Markdown')

    # Move to next word
    context.user_data['current_practice_index'] += 1
    index += 1

    if index < len(words):
        next_word = words[index]
        # Randomize translation direction for the next word
        translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
        context.user_data['practice_translation_direction'] = translation_direction  # Update direction
        if translation_direction == 'uzbek_to_english':
            prompt = f"📝 *Translate to English:* {next_word[1]}"
        else:
            prompt = f"📝 *Translate to Uzbek:* {next_word[2]}"
        await update.message.reply_text(prompt, parse_mode='Markdown')
        return PRACTICE_COMMUNICATE
    else:
        # User has completed all words, show summary
        correct = context.user_data.get('practice_correct_answers', 0)
        incorrect = context.user_data.get('practice_incorrect_answers', 0)
        total = correct + incorrect

        # Calculate percentage
        if total > 0:
            percentage = (correct / total) * 100
        else:
            percentage = 0

        # Generate feedback based on performance
        if percentage == 100:
            feedback = "🎯 *Excellent!* You got all answers correct!"
        elif percentage >= 80:
            feedback = "👍 *Great job!* You scored highly."
        elif percentage >= 50:
            feedback = "🙂 *Good effort!* Keep practicing to improve."
        else:
            feedback = "🧐 *Needs Improvement.* Don't give up and keep learning!"

        summary = (
            f"🎉 *Practice Session Completed!*\n\n"
            f"✅ *Correct Answers:* {correct}\n"
            f"❌ *Incorrect Answers:* {incorrect}\n"
            f"📊 *Score:* {percentage:.2f}%\n\n"
            f"{feedback}"
        )

        await update.message.reply_text(summary, parse_mode='Markdown')

        # Return to Admin Menu
        keyboard = [
            [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
            [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
            [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
            [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
            [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADMIN_MENU

# User Communication - Receive Answer
async def user_communicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip().lower()
    words = context.user_data.get('user_words')
    index = context.user_data.get('current_word_index')
    translation_direction = context.user_data.get('translation_direction')

    if index >= len(words):
        # This should not happen, but handle it gracefully
        await update.message.reply_text("🎉 *You've already completed all words in this subject.*", parse_mode='Markdown')
        return ConversationHandler.END

    current_word = words[index]

    if translation_direction == 'uzbek_to_english':
        correct_answer = current_word[2].lower()
        prompt = f"📝 *Translate to English:* {current_word[1]}"
    else:
        correct_answer = current_word[1].lower()
        prompt = f"📝 *Translate to Uzbek:* {current_word[2]}"

    if user_answer == correct_answer:
        context.user_data['correct_answers'] += 1
        await update.message.reply_text("✅ *Correct!* 🎉", parse_mode='Markdown')
    else:
        context.user_data['incorrect_answers'] += 1
        await update.message.reply_text(f"❌ *Incorrect.* The correct answer is: `{correct_answer}`", parse_mode='Markdown')

    # Move to next word
    context.user_data['current_word_index'] += 1
    index += 1

    if index < len(words):
        next_word = words[index]
        # Randomize translation direction for the next word
        translation_direction = random.choice(['uzbek_to_english', 'english_to_uzbek'])
        context.user_data['translation_direction'] = translation_direction  # Update direction
        if translation_direction == 'uzbek_to_english':
            prompt = f"📝 *Translate to English:* {next_word[1]}"
        else:
            prompt = f"📝 *Translate to Uzbek:* {next_word[2]}"
        await update.message.reply_text(prompt, parse_mode='Markdown')
        return USER_COMMUNICATE
    else:
        # User has completed all words, show summary
        correct = context.user_data.get('correct_answers', 0)
        incorrect = context.user_data.get('incorrect_answers', 0)
        total = correct + incorrect

        # Calculate percentage
        if total > 0:
            percentage = (correct / total) * 100
        else:
            percentage = 0

        # Generate feedback based on performance
        if percentage == 100:
            feedback = "🎯 *Excellent!* You got all answers correct!"
        elif percentage >= 80:
            feedback = "👍 *Great job!* You scored highly."
        elif percentage >= 50:
            feedback = "🙂 *Good effort!* Keep practicing to improve."
        else:
            feedback = "🧐 *Needs Improvement.* Don't give up and keep learning!"

        summary = (
            f"🎉 *Session Completed!*\n\n"
            f"✅ *Correct Answers:* {correct}\n"
            f"❌ *Incorrect Answers:* {incorrect}\n"
            f"📊 *Score:* {percentage:.2f}%\n\n"
            f"{feedback}"
        )

        await update.message.reply_text(summary, parse_mode='Markdown')

        return ConversationHandler.END

# Cancel Handler with Redirect to Start
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 *Operation cancelled.*", parse_mode='Markdown')
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        # Send Admin Menu
        keyboard = [
            [InlineKeyboardButton("📖 Create Subject", callback_data='create_subject')],
            [InlineKeyboardButton("🗑️ Delete Subject", callback_data='delete_subject')],
            [InlineKeyboardButton("➕ Add Word", callback_data='add_word')],
            [InlineKeyboardButton("🗑️ Delete Word", callback_data='delete_word')],
            [InlineKeyboardButton("🧑‍🏫 Practice", callback_data='practice')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📌 *Admin Menu:*', parse_mode='Markdown', reply_markup=reply_markup)
        return ADMIN_MENU
    else:
        # Send User Menu
        subjects = db.get_subjects()
        if not subjects:
            await update.message.reply_text("❌ No subjects available. Please contact the admin.")
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(subject, callback_data=f'user_subject_{subject}')] for subject in subjects]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('📚 *Choose a Subject to Practice:*', parse_mode='Markdown', reply_markup=reply_markup)
        return USER_SELECT_SUBJECT

# Main Function to Run the Bot
def main():
    # Build the application without persistence
    application = ApplicationBuilder().token(TOKEN).build()

    # Define Conversation Handler for Admin
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADMIN_MENU: [CallbackQueryHandler(admin_menu_callback)],
            CREATE_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_subject)],
            DELETE_SUBJECT: [CallbackQueryHandler(delete_subject_callback)],
            ADD_WORD_SELECT_SUBJECT: [CallbackQueryHandler(add_word_select_subject_callback)],
            ADD_WORD_UZBEK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_word_receive_uzbek)],
            ADD_WORD_ENGLISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_word_receive_english)],
            DELETE_WORD_SELECT_SUBJECT: [CallbackQueryHandler(delete_word_select_subject_callback)],
            DELETE_WORD_SELECT_WORD: [CallbackQueryHandler(delete_word_confirm)],
            PRACTICE_SELECT_SUBJECT: [CallbackQueryHandler(practice_select_subject_callback)],  # New Practice State
            PRACTICE_COMMUNICATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, practice_communicate)]  # New Practice Communication State
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False  # Ensures CallbackQueryHandlers are tracked for every message
        # Removed 'name' and 'persistent' parameters
    )

    # Define Conversation Handler for User
    user_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USER_SELECT_SUBJECT: [CallbackQueryHandler(user_select_subject_callback)],
            USER_COMMUNICATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_communicate)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False  # Ensures CallbackQueryHandlers are tracked for every message
        # Removed 'name' and 'persistent' parameters
    )

    # Add handlers
    application.add_handler(admin_conv_handler)
    application.add_handler(user_conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
