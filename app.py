from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Client, Projet

app = Flask(__name__)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elec_pro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'une_cle_tres_secrete_123'

# Initialisation de la base de données
db.init_app(app)

# Création des tables au démarrage
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # On récupère tous les clients pour les afficher sur le dashboard
    tous_les_clients = Client.query.all()
    nombre_clients = len(tous_les_clients)
    return render_template('index.html', clients=tous_les_clients, total=nombre_clients)

@app.route('/ajouter_client', methods=['GET', 'POST'])
def ajouter_client():
    if request.method == 'POST':
        nom = request.form.get('nom_complet')
        tel = request.form.get('telephone')
        adresse = request.form.get('adresse')
        
        # On crée le client (lié par défaut à l'utilisateur 1)
        nouveau_client = Client(nom_complet=nom, telephone=tel, adresse_chantier=adresse, user_id=1)
        
        db.session.add(nouveau_client)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('Ajouter_client.html')
@app.route('/devis/<int:client_id>', methods=['GET', 'POST'])
def creer_devis(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        # Récupération des données du formulaire
        article = request.form.get('designation')
        qte = int(request.form.get('quantite'))
        prix = float(request.form.get('prix_unitaire'))
        
        nouveau_materiel = MaterielDevis(designation=article, quantite=qte, prix_unitaire=prix, client_id=client_id)
        db.session.add(nouveau_materiel)
        db.session.commit()
        return redirect(url_for('creer_devis', client_id=client_id))
    
    materiels = MaterielDevis.query.filter_by(client_id=client_id).all()
    total_devis = sum(m.quantite * m.prix_unitaire for m in materiels)
    
    return render_template('creer_devis.html', client=client, materiels=materiels, total=total_devis)
    
if __name__ == "__main__":
    import os
    # Render utilise une variable d'environnement nommée PORT
    port = int(os.environ.get("PORT", 5000))
    # On lance l'application sur le port fourni par Render
    app.run(host='0.0.0.0', port=port)
    