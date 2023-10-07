from flask import Flask,redirect,render_template, url_for, request, session, send_from_directory
import psycopg2
import os
import tri



######################
### Initialisation ###
######################

# Nom de l'application
app = Flask(__name__)

# Variable utilisée pour la session
app.secret_key = os.urandom(24)

# Tris et filtres sélectionnés
tris = {}
tris['recents'] = 'checked'
tris['urgents'] = ''
tris['populaires'] = ''
tris['termines'] = ''
tris['avis'] = ''

@app.teardown_appcontext
def close_connection(exception):
    """Ferme la connexion à la base de donnée à l'arrêt du serveur web"""
    get_db().close()



######################
### Page d'accueil ###
######################

@app.route('/')
def Main():
    """Affiche la liste des posts selon les tris et filtres sélectionnés"""
    return render_template('template.html', page='liste_posts.html', posts=get_posts(), tri=tris)



@app.route('/<filtre>')
def filtrer(filtre='recents'):
    """Mets à jour les liste des tris et filtres sélectionnés"""

    # Test si le paramètre est un tri
    if filtre in ['recents', 'urgents', 'populaires']:
        # Remplace le tri précédent par le tri choisi
        for filtres in ['recents', 'urgents', 'populaires']:
            tris[filtres]='' 
        tris[filtre]='checked'

    # Test si le paramètre est un filtre
    if filtre in ['termines', 'avis']:
        # Sélectionne ou désélectionne le filtre choisi selon sont état précédent
        if tris[filtre]=='checked':
            tris[filtre]=''
        else:
            tris[filtre]='checked'

    # Redirige vers la page affichant la liste des tris
    return redirect(url_for('Main'))



### Fonction page d'accueil ###

def get_posts():
    """Renvoie la liste des posts selons les filtres et tris sélectionnés"""

    # Requete de base
    requete = "select json_build_object('id', posts.post_id, 'titre', titre, 'utilisateur_id', posts.utilisateur_id, 'auteur', auteur, 'texte', texte, 'date_fin', date_fin, 'statut', statut) from posts"
    
    # Construit la requête selon les filtres et tris sélectionnés
    if session and tris['avis'] == 'checked':
        requete += f" inner join avis on posts.post_id=avis.post_id where avis.utilisateur_id = {session['id']}"
    if tris['termines']!='checked':
        requete += (" where" if not(session and tris['avis'] == 'checked') else " and")+" statut = true"
    if tris['recents'] == 'checked':
        requete += " order by date_debut desc"
    elif tris['urgents'] == 'checked':
        requete += " order by (case when date_fin < current_date then 1 else 0 end), date_fin"
    elif tris['populaires'] == 'checked':
        requete += " order by nb_avis desc"

    # Execute la requête
    c = get_db().cursor()
    c.execute(requete)

    # Renvoie la liste des posts
    return to_liste(c.fetchall())








#########################
### Gestion des posts ###
#########################

@app.route('/post/<id>')
def voir_post(id):
    """Affiche la page de visualisation d'un post"""

    # Récupère le post dans la base de données
    c = get_db().cursor()
    c.execute(f"select json_build_object('id', post_id, 'titre', titre, 'auteur', auteur, 'texte', texte, 'date_fin', date_fin, 'statut', statut, 'nb_avis', nb_avis) from posts where post_id = {id}")
    post = c.fetchone()[0]

    # Redirige vers la page d'accueil si l'identifiant passé en paramètre n'est pas valide
    if not post:
        return redirect(url_for('Main'))

    # Récupère l'avis de l'utilisateur connecté sur le post
    get_avis_utilisateur(post)

    # Récupère le nombre d'avis sur le post
    get_avis(post)

    # Récupère les commentaires sur le post
    c.execute(f"select json_build_object('id', commentaire_id, 'utilisateur_id', utilisateur_id, 'auteur', auteur, 'texte', texte, 'date', date_commentaire, 'supprime', supprime, 'avis', avis) from premiers where post_id = {post['id']} order by date_commentaire desc, commentaire_id desc")
    post['commentaires'] = to_liste(c.fetchall())

    # Initiallise le compte de commentaires positifs/neutres/négatifs
    post['avis_commentaires'] = {'positif': 0, 'neutre': 0, 'negatif': 0}
    
    # Vérifie qu'il y a des commentaires
    if post['commentaires']:

        # Parcours les commentaires
        for com in post['commentaires']:
            
            # Ajoute l'avis du commentaire au total
            post['avis_commentaires'][com['avis']] += 1

            # Récupère les réponses au commentaire
            c.execute(f"select json_build_object('id', commentaire_id, 'utilisateur_id', utilisateur_id, 'auteur', auteur, 'texte', texte, 'date', date_commentaire, 'supprime', supprime, 'avis', avis) from reponses where premier_id = {com['id']} order by date_commentaire, commentaire_id")
            com['reponses'] = to_liste(c.fetchall())

    # Affiche la page de visualisation du post
    return(render_template('template.html', page='voir_post.html', post=post))



@app.route('/nouveau_post', methods=["GET","POST"])
def nouveau_post():
    """Affiche la page de création d'un post et crée un post """

    # Vérifie qu'un utilisateur est connecté
    if not est_connecte():
        return redirect(url_for('Main'))

    # Vérifie si un formulaire de création d'un post a été rempli
    if request.method == 'POST' :

        # Ajoute le post à la base de données et récupère l'identifiant du post
        img = ajouter_post_db(request.form['Titre'], request.form['Texte'], session['id'], request.form['date_fin'])

        # Sauvegarde l'image donnée avec pour nom l'identifiant du post
        image = request.files['Img']
        if image.filename != '':
            image.save(os.path.join('images_posts', img))

        # Renvoie vers la page du post ajouté
        return redirect(url_for('voir_post', id=img)) 
    
    # Renvoie vers la page de création d'un post
    return render_template('template.html', page='nouveau_post.html')    



@app.route('/supprimer/<id>/<auteur>')
def supprimer(id, auteur):
    """Supprime un post"""

    # Vérifie que l'utilisateur connecté est l'auteur du post
    if est_utilisateur_connecte(auteur) or est_administrateur():

        # Supprime le post de la base de données
        db = get_db()
        c = db.cursor()
        c.execute(f"delete from posts where post_id = {id}")
        db.commit()

        # Supprime l'image du post si elle existe
        if os.path.exists(os.path.join('images_posts', id)):
            os.remove(os.path.join("images_posts", id))

    # Redirige vers la page d'accueil
    return redirect(url_for('Main'))



### Routes complémentaires gestion des posts ###

@app.route('/avis/<post>/<avis>')
def avis(post, avis):
    """Ajoute un avis à un post"""

    # Vérifie que l'utilisateur est connecté et que l'avis transmis en paramètre est valide
    if est_connecte() and avis in ['Pour', 'Indifférent', 'Contre']:

        # Ajoute l'avis à la base de données ou met à jour l'avis existant
        db = get_db()
        c = db.cursor()
        c.execute('INSERT INTO avis (utilisateur_id, post_id, avis) VALUES(%s, %s, %s) ON conflict (utilisateur_id, post_id) DO UPDATE set avis=excluded.avis', (session['id'], post, avis))
        db.commit()
    
    # Redirige vers la page de visualisation du post sur lequel l'avis a été donné
    return redirect(f"/post/{post}")



@app.route('/images_posts/<filename>')
def get_image_post(filename=''):
    """Renvoie l'image dont le nom est passé en paramètre"""

    # Vérifie que l'image existe
    if os.path.exists(os.path.join('images_posts', filename)):
        # Renvoie l'image trouvée
        return send_from_directory('images_posts', filename)
    else:
        #Renvoie l'image par défaut
        return send_from_directory('images_posts', 'no_image.png')



### Fonctions de gestion des post ###

def ajouter_post_db(titre, texte, auteur, date_fin):
    """Ajoute un post avec les données passées en paramètre à la base de donnée et renvoie l'identifiant du post ajouté"""

    db = get_db()
    c = db.cursor()

    # Dissocie les cas selon qu'une date de fin ai été fournise ou non
    if date_fin =='':
        c.execute('INSERT INTO posts (titre, auteur, texte) VALUES (%s, %s, %s) returning utilisateur_id',(titre, auteur, texte))
    else: 
        c.execute('INSERT INTO posts (titre, auteur, texte, date_fin) VALUES (%s, %s, %s, %s) returning utilisateur_id',(titre, auteur, texte, date_fin))
    
    # Récupère l'identifiant du post pour nommer l'image du post
    id = c.fetchone()[0]
    db.commit()

    # Renvoie l'identifiant
    return str(id)



def get_avis_utilisateur(post):
    """Ajoute au post passé en paramètre l'avis de l'utilisateur connecté"""
    # Vérifie que l'utilisateur est connecté
    if not est_connecte():
        return

    # Récupère l'avis sur le post donné par l'utilisateur connecté
    c = get_db().cursor()
    c.execute(f"select avis from avis where post_id = {post['id']} and utilisateur_id = {session['id']}")
    avis = c.fetchone()

    # Vérifie si un avis a été donné
    if avis:

        # Place la variable utilisée pour mettre en évidence l'avis donné à la largeur de la bordure
        for a in ['Pour', 'Indifférent', 'Contre']:
            if avis[0]==a:
                post[a] = '3'
            else:
                post[a] = '1'



def get_avis(post):
    """Récupère le nombre d'avis d'un post"""

    # Récupère le nombre d'avis "Pour", "Indifférent" et "Contre"
    c = get_db().cursor()   
    c.execute(f"select json_build_object('pour', count(*) filter (where avis = 'Pour'), 'indifferent', count(*) filter (where avis = 'Indifférent'), 'contre', count(*) filter (where avis = 'Contre')) from avis where post_id = {post['id']} group by post_id")
    avis = c.fetchone()

    # Vérifie si des avis ont déjà été donnés
    if avis:
        # Ajoute les avis au post
        post['avis'] = avis[0]  
    else:
        # Place à 0 les nombres d'avis'
        post['avis'] = {'pour': 0, 'indifferent': 0, 'contre': 0}






####################
### Commentaires ###
####################

def get_avis_du_commentaire(com):
    """Renvoie si le commentaire est positif, neutre ou négatif"""

    # Détermine si le commentaire est postif, neutre ou négatif
    avis = tri.avis_commentaire(com)

    if avis < 0:
        avis = "negatif"
    elif avis > 0:
        avis = "positif"
    else:
        avis = "neutre"
    
    return avis

@app.route('/commenter_post', methods=["GET","POST"])
def commenter_post():
    """Ajoute un commentaire à un post"""

    # Vérifie que l'utilisateur est connecté
    if not est_connecte():
        return redirect(url_for('Main'))

    # Vérifie que le formulaire a été remplis
    if request.method == 'POST' :

        # Post commenté
        post = request.form['post']
        # Contenu du commentaire
        texte = request.form['commentaire']
        # Identifiant de l'utilisateur commentant
        auteur = session['id']

        # Détermine si le commentaire est postif, neutre ou négatif
        avis = get_avis_du_commentaire(request.form['commentaire'])

        # Ajoute le commentaire à la base de données
        db = get_db()
        c = db.cursor()
        c.execute('INSERT INTO premiers (post_id, utilisateur_id, texte, avis) VALUES (%s, %s, %s, %s)',(post, auteur, texte, avis))
        db.commit()

        # Redirige vers la page de visualisation du post commenté
        return redirect(f"/post/{post}") 
    
    # Redirige vers la page d'accueil
    return redirect(url_for('Main'))

@app.route('/repondre_commentaire', methods=["GET","POST"])
def repondre_commentaire():
    """Ajoute une réponse au commentaire d'un post"""

    # Vérifie que l'utilisateur est connecté
    if not est_connecte():
        return redirect(url_for('Main'))

    # Vérifie que le formulaire a été remplis
    if request.method == 'POST' :

        # Post du commentaire répondu
        post = request.form['post']
        # Commentaire répondu
        commentaire = request.form['id']
        # Contenu de la réponse
        texte = request.form['commentaire']
        # Identifiant de l'utilisateur répondant
        auteur = session['id']

        # Détermine si la réponse est postive, neutre ou négative
        avis = get_avis_du_commentaire(request.form['commentaire'])

        # Ajoute la réponse à la base de données
        db = get_db()
        c = db.cursor()
        c.execute('INSERT INTO reponses (premier_id, utilisateur_id, texte, avis) VALUES (%s, %s, %s, %s)',(commentaire, auteur, texte, avis))
        db.commit()

        # Redirige vers la page de visualisation du post du comentaire répondu
        return redirect(f"/post/{post}") 
    
    # Redirige vers la page d'accueil
    return redirect(url_for('Main'))

@app.route('/supprimer_commentaire/<post>/<id>/<commentaire>')
def supprimer_commentaire(post, id, commentaire):
    """Déclare un commentaire ou une réponse à un commentaire de la base de données comme étant supprimé"""

    # Vérifie que l'utilisateur connecté est l'auteur du commentaire ou de la réponse
    if est_utilisateur_connecte(id) or est_administrateur():

        # Supprime le commentaire de la base de données
        db = get_db()
        c = db.cursor()
        c.execute(f"delete from commentaires where commentaire_id = {commentaire}")
        db.commit()

        # Redirige vers la page de visualisation du post du comentaire ou de la réponse supprimé
        return redirect(f"/post/{post}") 

    # Redirige vers la page d'accueil
    return redirect(url_for('Main'))






#########################
### Gestion de profil ###
#########################

@app.route('/profil/<id>')
def profil(id):
    """Affiche le profil d'un utilisateur"""

    # Redirige vers la page d'accueil si l'identifiant demandé ne correspond pas à un utilisateur
    if not est_utilisateur(id):
        return redirect(url_for("Main"))
    
    c=get_db().cursor()

    # Test si l'utilisateur est un particulier ou une administration et récupère ses informations
    if est_particulier(id):
        c.execute(f"select json_build_object('utilisateur_id', utilisateur_id, 'adresse', adresse, 'nom', nom, 'prenom', prenom) from particuliers where utilisateur_id = {id}")
    else:
        c.execute(f"select json_build_object('utilisateur_id', utilisateur_id, 'adresse', adresse, 'denomination', denomination, 'telephone', telephone, 'email', email, 'site', site) from administrations where utilisateur_id = {id}")
    utilisateur = c.fetchone()[0]    
    
    # Compte le nombre de posts de l'utilisateur
    c.execute(f"select count(*) from posts where utilisateur_id = {id}")
    utilisateur['posts'] = c.fetchone()[0]

    # Compte le nombre d'avis de l'utilisateur
    c.execute(f"select count(*) from avis where utilisateur_id = {id}")
    utilisateur['avis'] = c.fetchone()[0]

    # Compte le nombre de commentaires de l'utilisateur
    c.execute(f"select count(*) from premiers where utilisateur_id = {id}")
    utilisateur['commentaires'] = c.fetchone()[0]

    # Affiche la page de profil de l'utilisateur
    return render_template('template.html', page='profil.html', utilisateur=utilisateur)



@app.route('/modifier_profil/<id>', methods=['POST', 'GET'])
def modifier_profil(id): 
    """Modifie le profil avec les informations transmises via le formulaire"""

    # Vérifie que l'utilisateur connecté est l'utilisateur du profil et que le formulaire a été remplis
    if est_utilisateur_connecte(id) and request.method=='POST':
        
        # Nouveau numéro de téléphone
        telephone = request.form['telephone']
        # Nouvel email
        email = request.form['email']
        # Nouveau site
        site = request.form['site']

        db = get_db()   
        c = db.cursor()
        # Modifie le numéro de téléphone s'il a été changé
        if telephone:
            c.execute(f"update administration set telephone=%s where administration_id = {id}", (telephone,))
        # Modifie l'email s'il a été changé
        if email:
            c.execute(f"update administration set email=%s where administration_id = {id}", (email,))
        # Modifie le site s'il a été changé
        if site:
            c.execute(f"update administration set site=%s where administration_id = {id}", (site,))
        db.commit()

        # Redirige vers la page du profil modifié
        return redirect(f"/profil/{id}") 
    
    # Redirige vers la page d'accueil
    return redirect(url_for('Main'))






#################
### Connexion ###
#################

@app.route('/log_in/<id>/<path:origine>')
def log_in(id, origine):
    """Connecte l'utilisateur sur un compte par défaut"""

    # Place la variable de session id
    session['id'] = int(id)

    # Connecte sur le compte de l'administration
    if int(id)==2:
        # Dénomination de l'administration
        session['username'] = 'Ville de Nancy'
        # Variable qui indique que l'utilisateur connecté est une administration
        session['admin'] = True

    # Connecte sur le compte d'un utilisateur
    else:
        # Nom de l'utilisateur
        session['username'] = 'François DENES'

    try:
        # Redirige vers la page où était l'utilisateur quand il s'est connecté
        return redirect("/"+origine)
    
    # Redirige vers la page d'accueil en cas d'erreur
    except Exception:
        return redirect(url_for('Main'))

@app.route('/log_out/<path:origine>')
def log_out(origine):
    """Déconnecte l'utilisateur"""

    # Supprime les variables de session
    session.clear()

    try:
        # Redirige vers la page où était l'utilisateur quand il s'est déconnecté
        return redirect("/"+origine)
    
    # Redirige vers la page d'accueil en cas d'erreur
    except Exception:
        return redirect(url_for('Main'))






########################
### Fonctions utiles ###
########################

def get_db():
    """Renvoie une instance de connexion à la base de données"""

    # Connecte à la base de données
    conn = psycopg2.connect(
        host="localhost",
        database="PPII",
        user="postgres",
        password="admin")
    
    # Renvoie la connexion établie
    return conn



@app.template_filter()
def format_datetime(value):
    """Passe une chaine de caractères représentant une date du format aaaa-mm-dd au format dd/mm/aaaa"""

    # Divise la date en année/mois/jour
    date = value.split('-')

    # Reconstruit la date au bon format
    return f"{date[2]}/{date[1]}/{date[0]}"



def est_connecte():
    """Renvoie si l'utilisateur est connecté. Renvoie vrai si la variable 'session' est initialisée"""
    return session

@app.template_filter()
def est_administrateur():
    """Renvoie si l'utilisateur est administrateur. Renvoie vrai si la variable de session 'admin' est initialisée et à True"""
    return session and session['admin'] and session['admin']==True

def est_utilisateur_connecte(id):
    """Renvoie si l'identifiant passé en paramètre correspond à l'identifiant de l'utilisateur connecté"""
    return est_connecte() and int(id) == session['id']



def to_liste(res_requete):
    """Renvoie sous forme de liste le résultat d'une requête"""
    return [x[0] for x in res_requete]



def est_utilisateur(id):
    """Renvoie vrai si l'identifiant passé en paramètre correspond à un utilisateur"""

    # Récupère l'utilisateur correspondant à l'identifiant transmis
    c=get_db().cursor()
    c.execute(f"select utilisateur_id from utilisateurs where utilisateur_id = {id}")

    # Renvoie si un utilisateur a été trouvé ou non
    return c.fetchone()!=None



def est_particulier(id):
    """Renvoie vrai si l'identifiant passé en paramètre correspond à un particulier"""

    # Vérifie que l'utilisateur existe
    if not est_utilisateur(id):
        return False

    # Récupère le particulier avec l'identifiant demandé
    c=get_db().cursor()
    c.execute(f"select utilisateur_id from particuliers where utilisateur_id = {id}")
    
    # Renvoie si un particulier avec l'identifiant transmis a été trouvé ou non
    return c.fetchone()!=None