import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Client, Projet, MaterielDevis

app = Flask(__name__)

# Nouveau bloc à coller à la place
app.config['SECRET_KEY'] = 'cle_secrete_ernest_2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cette partie vérifie si on est sur Render ou en local
if os.environ.get('RENDER'):
    # Sur Render, on utilise le dossier /tmp qui autorise l'écriture
    db_path = os.path.join('/tmp', 'elec_pro.db')
else:
    # En local (Termux/PC), on reste dans le dossier du projet
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'elec_pro.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path


db.init_app(app)

with app.app_context():
    db.create_all()
    # Création d'un utilisateur par défaut si vide
    if not User.query.first():
        user_test = User(username="Ernest")
        db.session.add(user_test)
        db.session.commit()

@app.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients, total=len(clients))

@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter_client():
    if request.method == 'POST':
        nom = request.form.get('nom_complet')
        tel = request.form.get('telephone')
        adr = request.form.get('adresse')
        nouveau = Client(nom_complet=nom, telephone=tel, adresse_chantier=adr, user_id=1)
        db.session.add(nouveau)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('ajouter_client.html')

@app.route('/devis/<int:client_id>', methods=['GET', 'POST'])
def creer_devis(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        art = request.form.get('designation')
        qte = int(request.form.get('quantite'))
        pu = float(request.form.get('prix_unitaire'))
        nouveau_mat = MaterielDevis(designation=art, quantite=qte, prix_unitaire=pu, client_id=client_id)
        db.session.add(nouveau_mat)
        db.session.commit()
        return redirect(url_for('creer_devis', client_id=client_id))
    
    materiels = MaterielDevis.query.filter_by(client_id=client_id).all()
    total_devis = sum(m.quantite * m.prix_unitaire for m in materiels)
    return render_template('creer_devis.html', client=client, materiels=materiels, total=total_devis)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
        
