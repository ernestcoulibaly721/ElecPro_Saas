import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION DE LA BASE DE DONNÉES ---
app.config['SECRET_KEY'] = 'cle_secrete_ernest_elecpro_2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Gestion du chemin pour Render (dossier /tmp pour l'écriture)
if os.environ.get('RENDER'):
    db_path = os.path.join('/tmp', 'elec_pro.db')
else:
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'elec_pro.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

# --- MODÈLES (BASE DE DONNÉES) ---
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

# Création des tables au démarrage
with app.app_context():
    db.create_all()

# --- ROUTES (LOGIQUE) ---

@app.route('/')
def index():
    tous_les_clients = Client.query.all()
    return render_template('index.html', clients=tous_les_clients, total_clients=len(tous_les_clients))

@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter_client():
    if request.method == 'POST':
        nom = request.form.get('nom_complet')
        tel = request.form.get('telephone')
        adr = request.form.get('adresse')
        
        nouveau_client = Client(nom_complet=nom, telephone=tel, adresse_chantier=adr)
        db.session.add(nouveau_client)
        db.session.commit()
        return redirect(url_for('index'))
    
    # Rappel : le fichier sur GitHub doit s'appeler exactement comme ici
    return render_template('Ajouter_client.html')

@app.route('/creer_devis/<int:client_id>', methods=['GET', 'POST'])
def creer_devis(client_id):
    client = Client.query.get_or_404(client_id)
    
    if request.method == 'POST':
        desig = request.form.get('designation')
        qte = int(request.form.get('quantite'))
        prix = float(request.form.get('prix_unitaire'))
        
        nouvel_article = MaterielDevis(
            designation=desig, 
            quantite=qte, 
            prix_unitaire=prix, 
            client_id=client.id
        )
        db.session.add(nouvel_article)
        db.session.commit()
        return redirect(url_for('creer_devis', client_id=client.id))

    # Calcul du total général du devis
    materiels = MaterielDevis.query.filter_by(client_id=client.id).all()
    total_general = sum(m.quantite * m.prix_unitaire for m in materiels)
    
    return render_template('creer_devis.html', client=client, materiels=materiels, total=total_general)

if __name__ == '__main__':
    app.run(debug=True)
    
