import App

reponse = App.app.test_client().get('/')
assert reponse.status_code == 200

# Route OK
reponse = App.app.test_client().get('/', query_string={'filtre': 'recents'})
assert reponse.status_code == 200

# Ne change pas les filtres si filtre invalide
reponse = App.app.test_client().get('/', query_string={'filtre': 'test'})
assert reponse.status_code == 200
        
# Redirige vers la page d'accueil si id non trouvé
reponse = App.app.test_client().get('/post', query_string={'id': 'test'})
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/nouveau_post')
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/supprimer', query_string={'id': 'test', 'auteur': 'test'})
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/commenter_post')
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/repondre_commentaire')
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/supprimer_commentaire')
assert reponse.status_code == 302

# Redirige vers la page d'accueil si l'utilisateur donné n'est pas valide
reponse = App.app.test_client().get('/profil', query_string={'id': 'test'})
assert reponse.status_code == 302

# Redirige vers la page d'accueil si pas connecté
reponse = App.app.test_client().get('/modifier_profil')
assert reponse.status_code == 302

# Redirige vers la page donnée après avoir connecté
reponse = App.app.test_client().get('/log_in', query_string={'id': '1', 'path': '/'})
assert reponse.status_code == 302

# Redirige vers la page donnée après avoir déconnecté
reponse = App.app.test_client().get('/log_out', query_string={'path': '/'})
assert reponse.status_code == 302