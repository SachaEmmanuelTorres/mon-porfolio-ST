import qrcode

# --- CONFIGURATION ---
# URLs directes via GitHub Pages (plus rapide et propre pour mobile)
# NOTE : Assurez-vous que ces fichiers PDF sont bien présents à la RACINE de votre dépôt GitHub.
url_cv_fr = "https://sachaemmanueltorres.github.io/mon-porfolio-ST/CV_Sacha_Torres_20252_main_os.pdf"
url_resume_en = "https://sachaemmanueltorres.github.io/mon-porfolio-ST/Resume_Sacha_Torres_2025_Eng_main_os.pdf"

def creer_qr(url, nom_fichier):
    """
    Génère un QR code à partir d'une URL et le sauvegarde en image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H, # Haute correction pour permettre l'ajout d'un logo
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Création de l'image (noir sur blanc)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(nom_fichier)
    print(f"✅ Fichier créé : {nom_fichier}")

if __name__ == "__main__":
    print("🚀 Génération des QR Codes pour les CVs (URLs GitHub Pages)...")
    
    # Génération des deux fichiers
    creer_qr(url_cv_fr, "qr_cv_fr.png")
    creer_qr(url_resume_en, "qr_resume_en.png")
    
    print("\n✨ Terminé ! Les images sont prêtes.")
