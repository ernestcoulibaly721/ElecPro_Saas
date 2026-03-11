import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'cle_secrete_ernest_2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.environ.get('RENDER'):
    db_path = os.path.join('/tmp', 'elec_pro.db')
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'elec_pro.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

# --- MODÈLES ---
class Profil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_entreprise = db.Column(db.String(100), default="Mon Entreprise Élec")
    gerant = db.Column(db.String(100), default="Nom du Gérant")
    telephone = db.Column(db.String(20), default="+226 XX XX XX XX")

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    adresse_chantier = db.Column(db.String(200))
    materiels = db.relationship('MaterielDevis', backref='client', lazy=True)

class MaterielDevis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(200), nullable=False)
    quantite = db.Column(db.Integer, default=1)
    prix_unitaire = db.Column(db.Float, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)

with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter_client():
    if request.method == 'POST':
        nouveau = Client(
            nom_complet=request.form.get('nom_complet'),
            telephone=request.form.get('telephone'),
            adresse_chantier=request.form.get('adresse')
        )
        db.session.add(nouveau)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('Ajouter_client.html')

# --- LOGIQUE DE LIMITATION À 3 DEVIS ---

@app.route('/creer_devis/<int:client_id>', methods=['GET', 'POST'])
def creer_devis(client_id):
    profil = Profil.query.first()
    client = Client.query.get_or_404(client_id)
    
    # Vérification de la limite
    if profil.devis_count >= 3 and not profil.is_premium:
        return render_template('upgrade.html') # On le redirige vers une page de paiement
    
    if request.method == 'POST':
        # ... ton code actuel pour ajouter le matériel ...
        
        # Si c'est le premier article du devis, on peut incrémenter le compteur
        # ou on incrémente au moment de la génération du PDF
        pass
    ', methods=['GET', 'POST'])
def creer_devis(client_id):
    client = Client.query.get_or_404(client_id)
    profil = Profil.query.first() or Profil()
    if request.method == 'POST':
        item = MaterielDevis(
            designation=request.form.get('designation'),
            quantite=int(request.form.get('quantite')),
            prix_unitaire=float(request.form.get('prix_unitaire')),
            client_id=client.id
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('creer_devis', client_id=client.id))
    
    total = sum(m.quantite * m.prix_unitaire for m in client.materiels)
    return render_template('creer_devis.html', client=client, materiels=client.materiels, total=total, profil=profil)

@app.route('/mon_profil', methods=['GET', 'POST'])
def mon_profil():
    profil = Profil.query.first()
    if not profil:
        profil = Profil()
        db.session.add(profil)
        db.session.commit()
    if request.method == 'POST':
        profil.nom_entreprise = request.form.get('nom_entreprise')
        profil.gerant = request.form.get('gerant')
        profil.telephone = request.form.get('telephone')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('mon_profil.html', profil=profil)

if __name__ == '__main__':
    app.run(debug=True)
    
