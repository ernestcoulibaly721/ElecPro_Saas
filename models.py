from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Aspect Commercial : Type d'abonnement (Gratuit, Pro, Premium)
    plan = db.Column(db.String(20), default='Gratuit') 
    is_active = db.Column(db.Boolean, default=True)
    
    # Relation : Un électricien a plusieurs clients
    clients = db.relationship('Client', backref='electricien', lazy=True)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_complet = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    adresse_chantier = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relation : Un client peut avoir plusieurs chantiers/devis
    projets = db.relationship('Projet', backref='client', lazy=True)

class Projet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False) # Ex: "Installation Villa Koudougou"
    description = db.Column(db.Text)
    statut = db.Column(db.String(20), default='En cours') # En cours, Terminé, Payé
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
 class MaterielDevis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), 
nullable=False) # Ex: Disjoncteur 16A
    quantite = db.Column(db.Integer, default=1)
    prix_unitaire = db.Column(db.Float,
nullable=False)
    client_id = db.Column(db.Integer, 
db.ForeignKey('client.id'), nullable=False)
    