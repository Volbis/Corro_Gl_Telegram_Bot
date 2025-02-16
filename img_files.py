from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import difflib

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Chemin du JSON du compte de service
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# l'ID Drive du dossier parent
FOLDER_ID = os.getenv("FOLDER_ID")

# Vérifier que les variables d'environnement ont bien été récupérées
if not SERVICE_ACCOUNT_FILE:
    raise ValueError("Le fichier de compte de service n'a pas été trouvé. Assurez-vous que le fichier .env contient SERVICE_ACCOUNT_FILE.")
if not FOLDER_ID:
    raise ValueError("L'ID du dossier n'a pas été trouvé. Assurez-vous que le fichier .env contient FOLDER_ID.")

# Listes de matières pour chaque partie de chaque semestre
SEMESTRE_1_PARTIE_1 = [
    "Anglais", "Analyse Numérique", "Introduction aux Systèmes d'Exploitation",
    "Merise 1&2", "Structure des Données Complexes et Langage C",
    "Langage du WEB",
    "Organisation et Gestion des Entreprises"
]

SEMESTRE_1_PARTIE_2 = [
    "Français", "Optimisation Linéaire", "Introduction à LINUX/UNIX",
    "Programmation Orientée Objet (C++)", "Initiation à l'UML",
    "Méthodologie de création de site WEB", "Développement Personnel"
]

SEMESTRE_2_PARTIE_1 = [
    "Méthodologie de rédaction de mémoire", "Probabilité et statistique",
    "Graphes et applications", "JAVA", "Technologies XML", "Infographie",
    "Communication graphique"
]

SEMESTRE_2_PARTIE_2 = [
    "Réseaux et services", "Base de donnée", "English", "Génie Logiciel"
]

# Structure de données pour organiser les fichiers
structure = {
    "Semestre 1": {
        "Partie 1": {matiere: [] for matiere in SEMESTRE_1_PARTIE_1},
        "Partie 2": {matiere: [] for matiere in SEMESTRE_1_PARTIE_2}
    },
    "Semestre 2": {
        "Partie 1": {matiere: [] for matiere in SEMESTRE_2_PARTIE_1},
        "Partie 2": {matiere: [] for matiere in SEMESTRE_2_PARTIE_2}
    }
}

# Ensemble pour vérifier les doublons
seen_files = set()

# Trouver la matière la plus proche du nom donné.
def find_closest_subject_match(name, matieres):
    name_lower = name.lower()
    matches = difflib.get_close_matches(name_lower, [m.lower() for m in matieres], n=1, cutoff=0.6)
    if matches:
        return next(m for m in matieres if m.lower() == matches[0])
    return None

# Ajouter un fichier à la structure en évitant les doublons.
def add_file_to_structure(file, closest_match):
    file_key = (file["name"].strip().lower(), file["id"])
    # Vérifier si le fichier a déjà été ajouté
    if file_key not in seen_files:
        seen_files.add(file_key)
        if closest_match in SEMESTRE_1_PARTIE_1:
            structure["Semestre 1"]["Partie 1"][closest_match].append(file)
        elif closest_match in SEMESTRE_1_PARTIE_2:
            structure["Semestre 1"]["Partie 2"][closest_match].append(file)
        elif closest_match in SEMESTRE_2_PARTIE_1:
            structure["Semestre 2"]["Partie 1"][closest_match].append(file)
        elif closest_match in SEMESTRE_2_PARTIE_2:
            structure["Semestre 2"]["Partie 2"][closest_match].append(file)

# Ajouter les fichiers qui n'etaient pas reconnus et classés dans "Autres" à la structure
def dernier_ajout():
    fichiers_specifiques = {
        "Introduction aux Systèmes d'Exploitation": [
            {"name": "Examen Linux S1 2e Partie.jpg", "id": "1SPccQVp2uoTHdKmgHMxOL24hRjsYtlXC"},
            {"name": "Devoir de Linuxx.png", "id": "1tqLj7o2X7ONoN8Zt4sb39wHY5U3Ss4Sp"}
        ],
        "Merise 1&2": [
            {"name": "livre de MERISE.jpg", "id": "1wK1ScONK62cgNaWr9myO9FkLlE8fPmwM"},
            {"name": "1_MERISE_DiapoPPT_M2.png", "id": "1iaWZnDaFOiWoh5Czv84uqubNB3CvhmIN"},
            {"name": "5 Merise (2012_2013).jpg", "id": "1UGTKMDEo6aJacs_efse5UHi1qJdGEPGd"},
            {"name": "cours merise interressant.png", "id": "1niTXYK-mJrnbZcfVH8lJ_v6Xy34_Te0F"},
            {"name": "Merise_SIGL2_2017_2018.jpg", "id": "1JbaX99m8fx__Cn9QdFvfmQhtvOtgtUlt"},
            {"name": "Merise_2_SIGL2_2017_2018.png", "id": "1By5J8yuutROnog8fNpvowhIfqVSLWVTW"},
            {"name": "Devoir de Merise.jpg", "id": "1lQ23bzDtSRbtDbom0s9d9zZQT3nTU-dO"}
        ],
        "Langage du WEB (Architecture client serveur, XHTML/CSS, PHP)": [
            {"name": "LANGAGE WEB - Chapitre 1 et 2 2024.jpg", "id": "1yiaWCR6IAZBPhPHkGdeu7idP4wpURJnM"},
            {"name": "Examen final MCW.png", "id": "1DZqmK7qOekQG8Q758wDvaf4mNVx7B5Kk"},
            {"name": "Devoir web programme.jpg", "id": "1tzKHl0tvVpo7PGfBzHYVAiR3U3B6sCIx"}
        ],
        "Organisation et Gestion des Entreprises": [
            {"name": "Cours OGE 2023-2024.jpg", "id": "1GWgZTNe079pQW9kd4t04n7NEUlCdvIM9"},
            {"name": "SUJETS kambo.png", "id": "1PcY5u5AZ5yuiYdsA0PmoTNPDlUK2bWQ0"},
            {"name": "COURS OGE 2024-2025.jpg", "id": "1nopAwirvX3-lPaHk54DYRM1B2o4zsdhC"},
            {"name": "OGE.jpg", "id": "1b954j5EaN0QmhWxCo8q2q-eHZkDDAv72"},
            {"name": "Examen Gestion des entreprises.png", "id": "12cBRpcsuvnQLyACFjCvOMrPj57Y9Qq0F"}
        ],
        "Structures de Données et Algorithmes": [
            {"name": "ALGORIHM AND DATA STRUCTURE.jpg", "id": "17GUx-UvUTi70l-IMhf_KxdM9xiIXkoST"},
            {"name": "Structure de données.png", "id": "12Jd2nA8jpFaTF-rk40cn3rNqCGaJaPVL"},
            {"name": "ALGORITHM AND DATA STRUCTURE 2024.jpg", "id": "1258Pbiv9y0VXJyG9vJrzLd8MtBkh_zdx"}
        ],
        "Analyse Numérique": [
            {"name": "TD2 ANA NUM 2022.jpg", "id": "1NWx1XS3NHpaJQtAog3ISEhLnCiGsHPeN"},
            {"name": "Analyse Num Modifié.png", "id": "1Nzg_EF4e7sn4vpnMmtzGaiB1YItYyMoQ"},
            {"name": "Solution_7.jpg", "id": "1JmH37_LMBY5010xK-rVOcVVrfU0C59a0"},
            {"name": "TD 1 ana num 2023.png", "id": "1pfY0CBl5P259sk0L5bHrZ8Rphb3A_0_Y"}
        ],
        "Anglais": [
            {"name": "Past simple Vs Past continuous.jpg", "id": "1fP1N4HsuMXW_XztJ_SB9k2zW4LIKH5iH"},
            {"name": "Present Simple vs Present Perfect Progressive.png", "id": "1YdNdiXqfW7HyXEmpDaSK9SCJSAoP3_MO"},
            {"name": "Present-Simple-vs.-Progressive-exercises.jpg", "id": "1fbtUMNQ_1i6QbdbISfMc8ZyH3WnhDmlR"},
            {"name": "Past simple Vs Past perfect.png", "id": "1EbtZTrDKAEErY_zjf2YLEwOF1JjC4Huc"}
        ],
        "Français": [
            {"name": "Français 2e partie S1 Examen.jpg", "id": "18miHzWLFE9bkZ7NWmWD0MEZ5vg8J0qek"},
            {"name": "TEF.png", "id": "13gBPX3jnTcqWyTfN8QLzKP22B0uQyWmr"}
        ],
        "Introduction à LINUX/UNIX": [
            {"name": "Examen Linux S1 2e Partie.jpg", "id": "1SPccQVp2uoTHdKmgHMxOL24hRjsYtlXC"},
            {"name": "Devoir de Linuxx.png", "id": "1tqLj7o2X7ONoN8Zt4sb39wHY5U3Ss4Sp"}
        ],
        "Programmation Orientée Objet (C++)": [
            {"name": "C++ 2epartie S1 Examen.jpg", "id": "1J02FpRMI1HY8TJ3MFrA4osuje1uq-WJx"},
            {"name": "Examen 2e session S1 C++.png", "id": "1qSNQjhf2vKWJy7dxcXGz-WVhFNUPgO-d"}
        ],
        "Initiation à l'UML": [
            {"name": "UML.jpg", "id": "1t5cJPofeCBmrYVHP9ubY6Xb22JK7n28h"}
        ],
        "Développement Personnel": [
            {"name": "Dev personnel.jpg", "id": "1TmcHQ8ZQI0xRFWeTOVIrucMSec9otY68"}
        ],
        "Probabilité et Statistique": [
            {"name": "Proba stats.jpg", "id": "1A6c5Ru3BfaNlboz21KpOs4Uk0cFGsqjs"},
            {"name": "Devoir de Proba Stat.png", "id": "1D9FwEbzqUtBWTwqBksM7bN4fiXm5Vdj1"}
        ],
        "Méthodologie de création de site WEB": [
            {"name": "Examen final MCW.png", "id": "1DZqmK7qOekQG8Q758wDvaf4mNVx7B5Kk"},
            {"name": "Devoir web programme.jpg", "id": "1tzKHl0tvVpo7PGfBzHYVAiR3U3B6sCIx"},
            {"name": "Cours MCW.jpg", "id": "1yiaWCR6IAZBPhPHkGdeu7idP4wpURJnM"},
            {"name": "Devoir de MCW.jpg", "id": "1tzKHl0tvVpo7PGfBzHYVAiR3U3B6sCIx"}
        ],
        "Technologies XML": [
            {"name": "XML.jpg", "id": "1_8eHxuq_XuSSACkNwQKZ-4t4fRCLcN02"}
        ],
        "English": [
            {"name": "Past simple Vs Past continuous.jpg", "id": "1fP1N4HsuMXW_XztJ_SB9k2zW4LIKH5iH"},
            {"name": "Present Simple vs Present Perfect Progressive.png", "id": "1YdNdiXqfW7HyXEmpDaSK9SCJSAoP3_MO"},
            {"name": "Present-Simple-vs.-Progressive-exercises.jpg", "id": "1fbtUMNQ_1i6QbdbISfMc8ZyH3WnhDmlR"},
            {"name": "Past simple Vs Past perfect.png", "id": "1EbtZTrDKAEErY_zjf2YLEwOF1JjC4Huc"}
        ],
        "JAVA": [
            {"name": "JAVA.jpg", "id": "1q3J3X0Z2d3q1v3Q2lX5uX3Z9bJtZr2vR"},
            {"name": "Java 2e partie S2 Examen.jpg", "id": "1J02FpRMI1HY8TJ3MFrA4osuje1uq-WJx"},
            {"name": "Examen 2e session S1 C++.png", "id": "1qSNQjhf2vKWJy7dxcXGz-WVhFNUPgO-d"}
        ],
        "Méthodologie de rédaction de mémoire": [
            {"name": "Méthodologie de rédaction de mémoire.jpg", "id": "1t5cJPofeCBmrYVHP9ubY6Xb22JK7n28h"}
        ],
        "Graphes et applications": [
            {"name": "Graphes.jpg", "id": "16goKcMiEYFhoQVVCaI0bA_qikyuSVeNF"}
        ],
        "Base de donnée": [
            {"name": "Base de donnée.jpg", "id": "1t5cJPofeCBmrYVHP9ubY6Xb22JK7n28h"},
            {"name": "Examen BD.png", "id": "1D9FwEbzqUtBWTwqBksM7bN4fiXm5Vdj1"},
            {"name": "Developpement Base de Donnée Examen S2.jpg", "id": "1UwBf_ESbFDchmWlDXLIqLyXdmHsCelG9"}
        ],
        "Génie Logiciel": [
            {"name": "Génie Logiciel.jpg", "id": "1t5cJPofeCBmrYVHP9ubY6Xb22JK7n28h"},
            {"name": "Examen GL.png", "id": "1D9FwEbzqUtBWTwqBksM7bN4fiXm5Vdj1"}
        ],
        "Statistique": [
            {"name": "IMG-20210413-WA0016.jpg", "id": "1yOHrXiqGr3whlr2eHkQ4zPr068ZLwPiC"},
            {"name": "20210413_102743.jpg", "id": "1dfju5VRz7RC8O4CKr-qHfB0w1LgMKREq"},
            {"name": "20210413_102720.jpg", "id": "18M5BBh2Ur5CpcnLNyKuTERlkgJuIIYEK"},
            {"name": "IMG_20160929_135530.jpg", "id": "1EEepD0GGFyDKeJgFKadqSe8XA1BCYypw"},
            {"name": "IMG_20160929_135639.jpg", "id": "1rB5GOaS0J1l5Bx6V0R3FyycNbeGBSrqk"},
            {"name": "sa - Copie.jpg", "id": "10yKswWhl0uzYpBWXuaO7b90P_HGMBZ1w"},
            {"name": "sa.jpg", "id": "1kl9GS1oardqTl8gQDXobFSq9UHSVJr-q"},
            {"name": "s.jpg", "id": "1m8quUQIkxqwMdUkJqoUm_TfU72rixmf5"},
            {"name": "stati - Copie.jpg", "id": "1mHaZeW64YyeQXtFv9IXmuvCNS0OfLEFF"},
            {"name": "statistique&.jpg", "id": "1IpNAfL4Ak-sFVuhY12EBEgfIOu77E0lx"},
            {"name": "statistique& - Copie.jpg", "id": "1RBFIYZ3-cG7ZtUKdHWx9a82C6ioAeh0-"},
            {"name": "stat.jpg", "id": "1bT5bdp3ZYul6c2fYOhQWzxsAo1zOkmKf"},
            {"name": "stati.jpg", "id": "11tWeJisAo-UgqPs0ZmfJ5m_k4FCiJOUq"}
        ],
        "Système d'Exploitation": [
            {"name": "Examen Linux S1 2e Partie.jpg", "id": "1SPccQVp2uoTHdKmgHMxOL24hRjsYtlXC"},
            {"name": "Devoir de Linuxx.png", "id": "1tqLj7o2X7ONoN8Zt4sb39wHY5U3Ss4Sp"},
            {"name": "IMG_20171004_040642.jpg", "id": "1PC_Wcu7WpHuh3jI2pOGEIuMhalO7EneF"},
            {"name": "IMG_20171005_213242.jpg", "id": "1-802bsuNhLZcQrDEbc5rIYZXh7UHrAGg"},
            {"name": "IMG_20171005_213226.jpg", "id": "1WzGEFqUdvN6jTQLRrnrSwWJuBxH0qlGA"},
            {"name": "IMG_20171004_041024.jpg", "id": "1FcUa43HjKkrz5M0BMeBHIko0eSM4tUKI"},
            {"name": "IMG_20171004_040815.jpg", "id": "1myRpGgG-BSIrw3vUgPCeO78F80ORrwZE"},
            {"name": "IMG_20160929_134015.jpg", "id": "1JbBGYfboTZfhyhgs7zhkIRGwpwXFKRvz"}
        ],
        "Merise 1&2": [
            {"name": "livre de MERISE.jpg", "id": "1wK1ScONK62cgNaWr9myO9FkLlE8fPmwM"},
            {"name": "1_MERISE_DiapoPPT_M2.png", "id": "1iaWZnDaFOiWoh5Czv84uqubNB3CvhmIN"},
            {"name": "5 Merise (2012_2013).jpg", "id": "1UGTKMDEo6aJacs_efse5UHi1qJdGEPGd"},
            {"name": "cours merise interressant.png", "id": "1niTXYK-mJrnbZcfVH8lJ_v6Xy34_Te0F"},
            {"name": "Merise_SIGL2_2017_2018.jpg", "id": "1JbaX99m8fx__Cn9QdFvfmQhtvOtgtUlt"},
            {"name": "Merise_2_SIGL2_2017_2018.png", "id": "1By5J8yuutROnog8fNpvowhIfqVSLWVTW"},
            {"name": "Devoir de Merise.jpg", "id": "1lQ23bzDtSRbtDbom0s9d9zZQT3nTU-dO"}
        ],
        "Infographie": [
            {"name": "Terminator.psd", "id": "1teFVrmX8JBeRW2YDGsNcQ3QOIwHb6Q0s"},
            {"name": "Final.jpg", "id": "1bcmGu8aUBfxu_uCZqmhDpYFui-iuHV_c"},
            {"name": "visage.png", "id": "1f-5ORkDj-BZAW049iUJaKgpLZG7HVOpb"},
            {"name": "visage2.jpg", "id": "1t2FeFOOG2dV7islDw7PAegxCSkP2KukE"},
            {"name": "visage.jpg", "id": "1fho8ysOlgQws4iU8gwkMenlLH1Gd7fKJ"},
            {"name": "oeil.png", "id": "1BliqDjIfq6MVruhW-kD9veeD3g7e-6BB"},
            {"name": "Terminator.psd", "id": "1tkiGXeW5Gn5PCyS5498QJGhaOj9JAnb7"},
            {"name": "Vente de pneu.psd", "id": "1Xu6RVywVe7IOx1JPivh_AdwcqRVamVx1"},
            {"name": "Final.jpg", "id": "1rs7whO85E1t8ZCzJMj0llyBIIMa-rrpR"},
            {"name": "Pneu.jpg", "id": "1XLnQdcwnJSkPLU6ci6UabNsGKk4-HrLh"},
            {"name": "Dessin.jpg", "id": "1UXrF93GIUaRsxpNkcWjUIyTZaUlKpVum"},
            {"name": "Dessin.jpg", "id": "10Pdw4uWlsIiwzziYiGZ8n1VnR6Dv7L-T"},
            {"name": "Carte de visite recto.png", "id": "1vKuqHihyrBmBgQaBv1zAl7WWdLVHqZAD"},
            {"name": "Carte de visite verso.png", "id": "1BRD2dkzD1ZxDPjD3_EjGqlk3_VhingOf"},
            {"name": "Carte de visite verso.png", "id": "1ViAO8eOVvlaL3DYIGt0K9ARnpV7NjNxZ"},
            {"name": "Carte de visite recto.png", "id": "1hPIgNA2DIiOr7nrawJjczKnaP-LEQ3Sm"},
            {"name": "qrcode.png", "id": "1LDifwWPGvvbXrT4cMmomWWRKYC_yRq8V"},
            {"name": "logo-wide.png", "id": "1UWzkvipUDtBqNnYLNymgGIZVJ-bBxiUT"},
            {"name": "logo-wide.png", "id": "1qcKioO9xks1N1ydG1ORYgUcnURNijY8E"}
        ],
        "Communication graphique": [
            {"name": "IMG_20160929_135910.jpg", "id": "1X5AkNQdlsVsVxm4nE2Rzc7PwsNVQALZF"}
        ],
        "Réseaux et services": [
            {"name": "IMG_20160929_135649.jpg", "id": "1VjZIBUgRSN4SytG1RMrshK8kzWFLHCJh"},
            {"name": "IMG_20160929_135726.jpg", "id": "1PdeL0LVsaAUmZ5sgB9WHZ95wydVWo5pi"},
            {"name": "IMG_20160929_135723.jpg", "id": "1rr_PkIZL6vUdq-z8o8M3oAExJ6UDr-L8"},
            {"name": "IMG_20160929_135716.jpg", "id": "15-TK0BJpco3WNv8efNB-VouVhKrwMavN"}
        ]
    }

    for matiere, fichiers in fichiers_specifiques.items():
        for fichier in fichiers:
            file_key = (fichier["name"].strip().lower(), fichier["id"])
            if file_key not in seen_files:
                seen_files.add(file_key)
                if matiere in SEMESTRE_1_PARTIE_1:
                    structure["Semestre 1"]["Partie 1"][matiere].append(fichier)
                elif matiere in SEMESTRE_1_PARTIE_2:
                    structure["Semestre 1"]["Partie 2"][matiere].append(fichier)
                elif matiere in SEMESTRE_2_PARTIE_1:
                    structure["Semestre 2"]["Partie 1"][matiere].append(fichier)
                elif matiere in SEMESTRE_2_PARTIE_2:
                    structure["Semestre 2"]["Partie 2"][matiere].append(fichier)

    return fichiers_specifiques

# Liste les fichiers images dans un dossier et ses sous-dossiers.
def list_files_in_folder(service, folder_id, folder_name):
    """Liste les fichiers images dans un dossier et ses sous-dossiers."""
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get("files", [])

    for file in files:
        if file["mimeType"].startswith("png/") or file["mimeType"].startswith("jpeg/") or file["mimeType"].startswith("jpg/"):
            closest_match = find_closest_subject_match(file["name"], SEMESTRE_1_PARTIE_1 + SEMESTRE_1_PARTIE_2 + SEMESTRE_2_PARTIE_1 + SEMESTRE_2_PARTIE_2)
            if closest_match:
                add_file_to_structure(file, closest_match)
        elif file["mimeType"] == "application/vnd.google-apps.folder":
            list_files_in_folder(service, file["id"], file["name"].strip())

    # Ajouter les fichiers spécifiques à la structure
    fichiers_specifiques = dernier_ajout()
    for matiere, fichiers in fichiers_specifiques.items():
        for fichier in fichiers:
            file_key = (fichier["name"].strip().lower(), fichier["id"])
            if file_key not in seen_files:
                seen_files.add(file_key)
                if matiere in SEMESTRE_1_PARTIE_1:
                    structure["Semestre 1"]["Partie 1"][matiere].append(fichier)
                elif matiere in SEMESTRE_1_PARTIE_2:
                    structure["Semestre 1"]["Partie 2"][matiere].append(fichier)
                elif matiere in SEMESTRE_2_PARTIE_1:
                    structure["Semestre 2"]["Partie 1"][matiere].append(fichier)
                elif matiere in SEMESTRE_2_PARTIE_2:
                    structure["Semestre 2"]["Partie 2"][matiere].append(fichier)

# Fonction pour afficher l'arborescence des répertoires et des fichiers.
def print_folder_structure(folder_structure, indent=0):
    """Affiche l'arborescence des répertoires et des fichiers."""
    indent_str = "  " * indent
    print(f"{indent_str}{folder_structure['name']}/")
    for file in folder_structure["files"]:
        print(f"{indent_str}  ├── {file['name']} (ID: {file['id']})")
    for i, subfolder in enumerate(folder_structure["subfolders"]):
        if i == len(folder_structure["subfolders"]) - 1:
            print(f"{indent_str}  └── {subfolder['name']}/")
        else:
            print(f"{indent_str}  ├── {subfolder['name']}/")
        print_folder_structure(subfolder, indent + 2)

def organiser_structure(folder_structure):
    organised_structure = {
        "Semestre 1": {
            "Partie 1": {matiere: [] for matiere in SEMESTRE_1_PARTIE_1},
            "Partie 2": {matiere: [] for matiere in SEMESTRE_1_PARTIE_2}
        },
        "Semestre 2": {
            "Partie 1": {matiere: [] for matiere in SEMESTRE_2_PARTIE_1},
            "Partie 2": {matiere: [] for matiere in SEMESTRE_2_PARTIE_2}
        }
    }

    for file in folder_structure["files"]:
        closest_match = find_closest_subject_match(file["name"], SEMESTRE_1_PARTIE_1 + SEMESTRE_1_PARTIE_2 + SEMESTRE_2_PARTIE_1 + SEMESTRE_2_PARTIE_2)
        if closest_match:
            add_file_to_structure(file, closest_match)

    for subfolder in folder_structure["subfolders"]:
        subfolder_files = organiser_structure(subfolder)
        for semestre, parties in subfolder_files.items():
            for partie, matieres in parties.items():
                for matiere, files in matieres.items():
                    organised_structure[semestre][partie][matiere].extend(files)

    return organised_structure

# La fonction principale
def list_images():
    """Liste les fichiers images d'un dossier Drive et affiche leurs ID."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)

    list_files_in_folder(service, FOLDER_ID, "Root Folder")

    """total_files = 0

    for semestre, parties in structure.items():
        print(f"\n{semestre} :")
        for partie, matieres in parties.items():
            print(f"  {partie} :")
            for matiere, files in matieres.items():
                print(f"    {matiere} ({len(files)} fichiers) :")
                total_files += len(files)
                for file in files:
                    print(f"      - {file['name']} (ID: {file['id']})")

    print(f"\nTotal des fichiers : {total_files}")"""

    return structure

if __name__ == "__main__":
    list_images()
