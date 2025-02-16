from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, Application, CallbackContext, CallbackQueryHandler
from googleapiclient.discovery import build
from google.oauth2 import service_account
import io
from googleapiclient.http import MediaIoBaseDownload
from pdf_files import list_files
from img_files import list_images
from dotenv import load_dotenv
import os
import asyncio

# Constantes pour les émojis et le style
EMOJIS = {
    "welcome": "👋",
    "semester": "🗓️",
    "part": "📝",
    "subject": "📘",
    "pdf": "🗂️",
    "image": "🎨",
    "loading": "⏳",
    "success": "✅",
    "error": "❌",
    "back": "↩️",
    "menu": "🏠"
}

SEPARATORS = {
    "header": "••••••••••••••••••••••••••⧞⧞⧞⧞⧞••••••••••••••••••••••••••",
    "section": "─⊰⊱─⊰⊱─────────────────────────⊰⊱─⊰⊱─"
}

# Charger les variables d'environnement
load_dotenv()
BOT_TOKEN = os.getenv("BOT_API_KEY")
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
FETCH_FROM_DRIVE = os.getenv("FETCH_FROM_DRIVE", "True").lower() == "true"

# Configuration Google Drive
if FETCH_FROM_DRIVE:
    def get_drive_service():
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)

    drive_service = get_drive_service()
    PDF_FILES = list_files()
    IMG_FILES = list_images()
else:
    PDF_FILES = {}
    IMG_FILES = {}

# Structure des matières
MATIERES = {
    "Semestre 1": {
        "Partie 1": [
            "Anglais", "Analyse Numérique", "Introduction aux Systèmes d'Exploitation",
            "Merise 1&2", "Structure des Données Complexes et Langage C",
            "Langage du WEB",
            "Organisation et Gestion des Entreprises"
        ],
        "Partie 2": [
            "Français", "Optimisation Linéaire", "Introduction à LINUX/UNIX",
            "Programmation Orientée Objet (C++)", "Initiation à l'UML",
            "Méthodologie de création de site WEB", "Développement Personnel"
        ]
    },
    "Semestre 2": {
        "Partie 1": [
            "Méthodologie de rédaction de mémoire", "Probabilité et statistique",
            "Graphes et applications", "JAVA", "Technologies XML", "Infographie",
            "Communication graphique"
        ],
        "Partie 2": [
            "Réseaux et services", "Base de donnée", "English", "Génie Logiciel"
        ]
    }
}

class Steps:
    SEMESTER = "semester"
    PART = "part"
    SUBJECT = "subject"
    FILE_TYPE = "file_type"
    FILE = "file"

user_progress = {}

# Créer un fil d'Ariane basé sur la progression de l'utilisateur
async def create_breadcrumb(user_progress_data):
    breadcrumb = [f"{EMOJIS['menu']} Menu"]

    if "semester" in user_progress_data:
        breadcrumb.append(f"{EMOJIS['semester']} {user_progress_data['semester']}")
    if "part" in user_progress_data:
        breadcrumb.append(f"{EMOJIS['part']} {user_progress_data['part']}")
    if "subject" in user_progress_data:
        breadcrumb.append(f"{EMOJIS['subject']} {user_progress_data['subject']}")

    return " → ".join(breadcrumb)

# Gérer la commande /start
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_progress[user_id] = {"step": Steps.SEMESTER}

    welcome_message = f"""
{SEPARATORS['header']}
     🔥 *🎓 BIENVENUE SUR GL CORRO_BOT 🎓* 🔥
{SEPARATORS['header']}

📚 *Besoin de croiso chap* sans te perdre dans des centaines de fichiers ?
Ne cherche plus, je suis là pour *t’aider à trouver les documents qu'il te faut en quelques clics* ! 🚀

🤔 *Comment ça marche :*

📌 1. Sélectionnez un *semestre*
📌 2. Choisissez une *partie*
📌 3. Sélectionnez une *matière*
📌 4. Accédez aux *documents immédiatement*

⚡ *T'es prêt ? Corrotons.....* ⚡

"""

    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['semester']} {semester}",
                             callback_data=f"semester:{semester}")]
        for semester in MATIERES.keys()
    ]

    keyboard.append([InlineKeyboardButton(f"{EMOJIS['menu']} Menu Principal",
                                        callback_data="menu:main")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Afficher les fichiers avec une interface améliorée
async def display_files(query, user_id, value):
    semester = user_progress[user_id]["semester"]
    part = user_progress[user_id]["part"]
    subject = user_progress[user_id]["subject"]
    current_page = user_progress[user_id].get("current_page", 0)
    ITEMS_PER_PAGE = 8

    await show_loading_message(query)

    files = get_files(value, semester, part, subject)
    current_files, total_pages = paginate_files(files, current_page, ITEMS_PER_PAGE)

    keyboard = build_keyboard(current_files, value, current_page, total_pages)
    message_text = await create_message_text(user_progress[user_id], value, current_page, total_pages)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Afficher un message de chargement initial
async def show_loading_message(query):
    await query.message.edit_text(f"{EMOJIS['loading']} Chargement des fichiers en cours...")

# Récupérer les fichiers en fonction du type de fichier et des paramètres de l'utilisateur
def get_files(value, semester, part, subject):
    return get_safe_value(
        PDF_FILES if value == "pdf" else IMG_FILES,
        semester, part, subject,
        default=[]
    )

# Gérer la pagination des fichiers
def paginate_files(files, current_page, items_per_page):
    start_idx = current_page * items_per_page
    end_idx = start_idx + items_per_page
    current_files = files[start_idx:end_idx]
    total_pages = (len(files) + items_per_page - 1) // items_per_page
    return current_files, total_pages

# Construire le clavier complet avec les fichiers et les boutons de navigation
def build_keyboard(current_files, value, current_page, total_pages):
    keyboard = []
    current_row = []

    for i, file_info in enumerate(current_files):
        file_emoji = EMOJIS['pdf'] if value == 'pdf' else EMOJIS['image']
        truncated_name = truncate_text(file_info['name'], max_length=20)
        button_text = f"{file_emoji} {truncated_name}"
        current_row.append(
            InlineKeyboardButton(button_text, callback_data=f"file:{file_info['id']}")
        )

        if len(current_row) == 2 or i == len(current_files) - 1:
            keyboard.append(current_row)
            current_row = []

    nav_buttons = build_navigation_buttons(current_page, total_pages)
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append(build_global_navigation_buttons())

    return keyboard

# Construire les boutons de navigation entre les pages
def build_navigation_buttons(current_page, total_pages):
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data="page:prev"))
    nav_buttons.append(InlineKeyboardButton(f"{current_page + 1}/{total_pages}", callback_data="none"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="page:next"))
    return nav_buttons

# Construire les boutons de navigation globale
def build_global_navigation_buttons():
    return [
        InlineKeyboardButton(f"{EMOJIS['back']} Retour", callback_data="file:back"),
        InlineKeyboardButton(f"{EMOJIS['menu']} Menu Principal", callback_data="menu:main")
    ]

# Créer le texte du message avec le fil d'Ariane
async def create_message_text(user_progress, value, current_page, total_pages):
    breadcrumb = await create_breadcrumb(user_progress)
    return f"""
{SEPARATORS['header']}
{breadcrumb}
{SEPARATORS['header']}

📂 *Fichiers {value.upper()}*
*{user_progress['subject']}*
Page {current_page + 1}/{total_pages}

{SEPARATORS['section']}
"""

# Gérer les callbacks des boutons
async def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    print(f"Callback reçu - Action: {query.data}")
    print(f"État actuel de l'utilisateur: {user_progress.get(user_id, 'Non trouvé')}")

    if user_id not in user_progress:
        await query.message.reply_text(
            f"{EMOJIS['error']} Session expirée. Veuillez utiliser /start pour recommencer."
        )
        return

    data = query.data.split(":")
    action = data[0]
    value = data[1]

    if action == "menu" and value == "main":
        await handle_menu_return(query, user_id)
        return

    if action == "semester":
        await handle_semester_selection(query, user_id, value)
    elif action == "part":
        await handle_part_selection(query, user_id, value)
    elif action == "subject":
        await handle_subject_selection(query, user_id, value)
    elif action == "file_type":
        await handle_file_type_selection(query, user_id, value)
    elif action == "page":
        await handle_page_navigation(query, user_id, value)
    elif action == "file":
        await handle_file_selection(query, user_id, value)

    await query.answer()

# Gérer le retour au menu principal
async def handle_menu_return(query, user_id):
    user_progress[user_id] = {"step": Steps.SEMESTER}
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['semester']} {semester}",
                             callback_data=f"semester:{semester}")]
        for semester in MATIERES.keys()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        f"{EMOJIS['menu']} *Menu Principal*\nVeuillez sélectionner un semestre :",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Gérer la sélection du semestre
async def handle_semester_selection(query, user_id, value):
    if value in MATIERES:
        user_progress[user_id].update({
            "step": Steps.PART,
            "semester": value
        })
        keyboard = [
            [InlineKeyboardButton(f"{EMOJIS['part']} {part}",
                                callback_data=f"part:{part}")]
            for part in MATIERES[value].keys()
        ]
        keyboard.append([InlineKeyboardButton(f"{EMOJIS['menu']} Menu Principal",
                                            callback_data="menu:main")])

        breadcrumb = await create_breadcrumb(user_progress[user_id])
        message = f"""
{SEPARATORS['header']}
{breadcrumb}
{SEPARATORS['header']}

Veuillez choisir une partie :
"""
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Gérer la sélection de la partie
async def handle_part_selection(query, user_id, value):
    semester = user_progress[user_id]["semester"]
    if value in MATIERES[semester]:
        user_progress[user_id].update({
            "step": Steps.SUBJECT,
            "part": value
        })

        keyboard = []
        subjects = MATIERES[semester][value]
        for subject in subjects:
            keyboard.append([
                InlineKeyboardButton(f"{EMOJIS['subject']} {subject}",
                                   callback_data=f"subject:{subject}")
            ])

        keyboard.append([
            InlineKeyboardButton(f"{EMOJIS['back']} Retour", callback_data="semester:{semester}"),
            InlineKeyboardButton(f"{EMOJIS['menu']} Menu Principal", callback_data="menu:main")
        ])

        breadcrumb = await create_breadcrumb(user_progress[user_id])
        message = f"""
{SEPARATORS['header']}
{breadcrumb}
{SEPARATORS['header']}

Veuillez choisir une matière :
"""
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Gérer la sélection de la matière
async def handle_subject_selection(query, user_id, value):
    semester = user_progress[user_id]["semester"]
    part = user_progress[user_id]["part"]
    if value in MATIERES[semester][part]:
        user_progress[user_id].update({
            "step": Steps.FILE_TYPE,
            "subject": value
        })
        print(Steps.FILE_TYPE)

        keyboard = [
            [InlineKeyboardButton(f"{EMOJIS['pdf']} PDF", callback_data="file_type:pdf")],
            [InlineKeyboardButton(f"{EMOJIS['image']} Image", callback_data="file_type:image")],
            [InlineKeyboardButton(f"{EMOJIS['back']} Retour", callback_data=f"part:{part}"),
             InlineKeyboardButton(f"{EMOJIS['menu']} Menu Principal", callback_data="menu:main")]
        ]

        breadcrumb = await create_breadcrumb(user_progress[user_id])
        message = f"""
{SEPARATORS['header']}
{breadcrumb}
{SEPARATORS['header']}

Choisissez le type de fichier pour *{value}* :
"""
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Gérer la sélection du type de fichier
async def handle_file_type_selection(query, user_id, value):
    print("value is   :", value)
    user_progress[user_id].update({
        "step": Steps.FILE,
        "file_type": value,
        "current_page": 0
    })
    print("value is rr  :", value)
    await display_files(query, user_id, value)

# Gérer la navigation entre les pages
async def handle_page_navigation(query, user_id, value):
    if value == "next":
        user_progress[user_id]["current_page"] += 1
    elif value == "prev":
        user_progress[user_id]["current_page"] -= 1

    await display_files(query, user_id, user_progress[user_id]["file_type"])

# Gérer la sélection d'un fichier
async def handle_file_selection(query, user_id, value):
    if value == "back":
        await handle_previous_step(query, user_id)
        return

    loading_message = await query.message.edit_text(
        f"{EMOJIS['loading']} Téléchargement en cours...",
        parse_mode='Markdown'
    )

    if FETCH_FROM_DRIVE:
        try:
            # Récupérer les métadonnées du fichier
            file_metadata = drive_service.files().get(fileId=value, fields='name,mimeType').execute()
            print("file_metadata is:", file_metadata)
            original_filename = file_metadata.get('name', f"document_{value}")
            
            # Télécharger directement le fichier sans vérification de type
            file_data = await download_file(value)
            if file_data:
                await loading_message.edit_text(
                    f"{EMOJIS['success']} Téléchargement réussi! Envoi du fichier...",
                    parse_mode='Markdown'
                )

                # Envoyer le fichier avec son nom original
                await query.message.reply_document(
                    document=file_data,
                    filename=original_filename
                )

                await display_files(query, user_id, user_progress[user_id]['file_type'])
            else:
                await loading_message.edit_text(
                    f"{EMOJIS['error']} Erreur lors du téléchargement. Veuillez réessayer.",
                    parse_mode='Markdown'
                )
                await asyncio.sleep(2)
                await display_files(query, user_id, user_progress[user_id]['file_type'])

        except Exception as e:
            print(f"Erreur lors du téléchargement: {str(e)}")
            await loading_message.edit_text(
                f"{EMOJIS['error']} Une erreur est survenue : {str(e)}",
                parse_mode='Markdown'
            )
            await asyncio.sleep(2)
            await display_files(query, user_id, user_progress[user_id]['file_type'])
    else:
        await loading_message.edit_text(
            f"{EMOJIS['success']} Mode simulation : Téléchargement simulé",
            parse_mode='Markdown'
        )
        await asyncio.sleep(2)
        await display_files(query, user_id, user_progress[user_id]['file_type'])


# Gérer le retour à l'étape précédente
async def handle_previous_step(query, user_id):
    current_step = user_progress[user_id]["step"]

    if current_step == Steps.FILE:
        user_progress[user_id].update({
            "step": Steps.FILE_TYPE,
            "file_type": None
        })
        keyboard = [
            [InlineKeyboardButton(f"{EMOJIS['pdf']} PDF", callback_data="file_type:pdf")],
            [InlineKeyboardButton(f"{EMOJIS['image']} Image", callback_data="file_type:image")],
            [InlineKeyboardButton(f"{EMOJIS['back']} Retour", callback_data="menu:main")]
        ]

        breadcrumb = await create_breadcrumb(user_progress[user_id])
        message = f"""
{SEPARATORS['header']}
{breadcrumb}
{SEPARATORS['header']}

Choisissez un type de fichier :
"""
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

# Gérer la commande /stats
async def handle_stats_command(update: Update, context: CallbackContext) -> None:
    stats = get_file_statistics()
    message = format_message("Statistiques du Bot", stats)
    await update.message.reply_text(message, parse_mode='Markdown')

# Téléchargement d'un fichier depuis Google Drive
async def download_file(file_id: str) -> io.BytesIO:
    try:
        request = drive_service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        file.seek(0)
        return file
    except Exception as e:
        print(f"Erreur de téléchargement : {e}")
        return None

# Annulation de la conversation
async def cancel(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in user_progress:
        del user_progress[user_id]
    await update.message.reply_text(
        f"{EMOJIS['error']} Opération annulée. Utilisez /start pour recommencer.",
        parse_mode='Markdown'
    )

# Compter le nombre de fichiers (PDF et Images) par matière pour un semestre et une partie donnés
def count_files_by_subject(semester: str, part: str) -> dict:
    result = {}
    for subject in MATIERES[semester][part]:
        pdf_count = len(get_safe_value(PDF_FILES, semester, part, subject, default=[]))
        img_count = len(get_safe_value(IMG_FILES, semester, part, subject, default=[]))
        result[subject] = {
            'pdf': pdf_count,
            'images': img_count,
            'total': pdf_count + img_count
        }
    return result

# Retourner des statistiques globales sur les fichiers du bot
def get_file_statistics() -> dict:
    stats = {
        'total_pdf': 0,
        'total_images': 0,
        'subjects_with_files': 0,
        'empty_subjects': 0
    }

    for semester in MATIERES:
        for part in MATIERES[semester]:
            for subject in MATIERES[semester][part]:
                pdfs = len(get_safe_value(PDF_FILES, semester, part, subject, default=[]))
                imgs = len(get_safe_value(IMG_FILES, semester, part, subject, default=[]))

                stats['total_pdf'] += pdfs
                stats['total_images'] += imgs

                if pdfs + imgs > 0:
                    stats['subjects_with_files'] += 1
                else:
                    stats['empty_subjects'] += 1

    return stats

# Formater un message avec titre et contenu pour l'affichage dans Telegram
def format_message(title: str, content: dict, add_separators: bool = True) -> str:
    message = []

    if add_separators:
        message.append(SEPARATORS['header'])

    message.append(f"*{title}*\n")

    for key, value in content.items():
        if isinstance(value, dict):
            message.append(f"*{key}*:")
            for sub_key, sub_value in value.items():
                message.append(f"  • {sub_key}: {sub_value}")
        else:
            message.append(f"• {key}: {value}")

    if add_separators:
        message.append(SEPARATORS['section'])

    return "\n".join(message)

# Tronquer le texte à la longueur maximale
def truncate_text(text: str, max_length: int = 30) -> str:
    if len(text) <= max_length:
        return text
    # Ajuster la longueur pour tenir compte des points de suspension
    return text[:max_length-3] + "..."

# Accès sécurisé aux valeurs imbriquées
def get_safe_value(dictionary, *keys, default=None):
    try:
        result = dictionary
        for key in keys:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default

# Fonction principale pour démarrer le bot
def main() -> None:
    print(f"{EMOJIS['loading']} Démarrage du bot...")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(handle_callback))

    print(f"{EMOJIS['success']} Bot démarré avec succès!")
    application.run_polling()

if __name__ == '__main__':
    main()
