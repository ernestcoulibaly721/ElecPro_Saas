import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'elecpro_secret_key_2026'
# Utilisation de SQLite pour le stockage des données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elecpro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODÈLES DE DONNÉES ---

class Profil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_entreprise = db.Column(db.String(100), default="Mon Entreprise Élec")
    gerant = db.Column(db.String(100), default="Nom du Gérant")
    telephone = db.Column(db.String(20), default="+226 XX XX XX XX")
    # Nouveaux champs pour la gestion payante
    devis_count = db.Column(db.Integer, default=0)
    is_premium = db.Column(db.Boolean, default=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(100), nullable=False)
    adresse_chantier = db.Column(db.String(200))
    materiels = db.relationship('Materiel', backref='client', lazy=True, cascade="all, delete-orphan")

class Materiel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200), nullable=False)
    quantite = db.Column(db.Integer, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

# --- ROUTES ---

@app.route('/')
def index():
    profil = Profil.query.first()
    if not profil:
        profil = Profil()
        db.session.add(profil)
        db.session.commit()
    
    clients = Client.query.all()
    return render_template('index.html', clients=clients, profil=profil)

@app.route('/profil', methods=['GET', 'POST'])
def profil():
    profil = Profil.query.first()
    if request.method == 'POST':
        profil.nom_entreprise = request.form.get('nom_entreprise')
        profil.gerant = request.form.get('gerant')
        profil.telephone = request.form.get('telephone')
        db.session.commit()
        flash('Profil mis à jour !', 'success')
        return redirect(url_for('index'))
    return render_template('profil.html', profil=profil)

@app.route('/ajouter_client', methods=['POST'])
def ajouter_client():
    nom = request.form.get('nom_complet')
    adresse = request.form.get('adresse_chantier')
    if nom:
        nouveau_client = Client(nom_complet=nom, adresse_chantier=adresse)
        db.session.add(nouveau_client)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/creer_devis/<int:client_id>', methods=['GET', 'POST'])
def creer_devis(client_id):
    profil = Profil.query.first()
    client = Client.query.get_or_404(client_id)
    
    # --- LOGIQUE DE BLOCAGE (TEST GRATUIT) ---
    # Si l'utilisateur n'est pas premium et a déjà fait 3 devis ou plus
    if not profil.is_premium and profil.devis_count >= 3:
        return render_template('upgrade.html', profil=profil)

    if request.method == 'POST':
        designation = request.form.get('designation')
        quantite = int(request.form.get('quantite', 1))
        prix = float(request.form.get('prix_unitaire', 0))
        
        # Si c'est le tout premier article de ce client, on compte ça comme un nouveau devis
        if not client.materiels:
            profil.devis_count += 1
        
        nouvel_article = Materiel(
            designation=designation, 
            quantite=quantite, 
            prix_unitaire=prix, 
            client_id=client.id
        )
        db.session.add(nouvel_article)
        db.session.commit()
        return redirect(url_for('creer_devis', client_id=client.id))
    
    materiels = client.materiels
    total = sum(m.quantite * m.prix_unitaire for m in materiels)
    
    return render_template('creer_devis.html', client=client, materiels=materiels, total=total, profil=profil)

@app.route('/supprimer_client/<int:client_id>')
def supprimer_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('index'))

# --- LANCEMENT ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
        
