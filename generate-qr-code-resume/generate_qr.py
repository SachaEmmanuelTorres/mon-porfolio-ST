import qrcode

# --- CONFIGURATION ---
# URLs directes via GitHub Pages avec les noms de fichiers exacts de votre capture d'écran
url_cv_fr = "https://sachaemmanueltorres.github.io/mon-porfolio-ST/CV_Sacha_Torres_20252_main_os.pdf"
url_resume_en = "https://sachaemmanueltorres.github.io/mon-porfolio-ST/Resume_Sacha_Torres_2025_Eng_main_os.pdf"

def creer_qr(url, nom_fichier):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(nom_fichier)
    print(f"✅ QR Code généré pour : {url} -> {nom_fichier}")

if __name__ == "__main__":
    print("🚀 Régénération des QR Codes avec les noms de fichiers validés...")
    creer_qr(url_cv_fr, "qr_cv_fr.png")
    creer_qr(url_resume_en, "qr_resume_en.png")
    print("\n✨ Terminé !")
