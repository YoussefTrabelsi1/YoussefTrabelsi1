from tri import find_words
from tri import analyse
from tri import avis_commentaire
from tri import avis

NEGATIF=['nul', 'nulle', 'détestable','horrible','laid','laide','méchant','affreux','idiot','débile','déception','tromper','insuffisante','invalidée',
          'stupide','ridicule','raté','médiocre','ennuyeux','pitoyable','effrayant','trompe','invalide','méchante','ratée','haïr','déçue',
          'dégoûtant','dégoûtante','mauvais','mauvaise','imbécile','déteste','hais','scandaliser','déçu','insuffisant','invalidé','affreuse','effrayante',
          'moque','dégoûte','effraie','effraye','ennuie','indigne','déçoit','injuste','imperfection','inefficace','ennuyeuse']

POSITIF=['génie','beau', 'belle', 'merveilleux','superbe', 'bien', 'bon', 'bonne', 'aimant','enthousiasmant','aimable','valide','prévoir',
          'distrayant','juste','aimable','réussi','reussie','parfait','délicieux','harmonieux','intélligent','prévois','aimante',
          'intélligence','apprécier','approuver','approuve','adorer','adore','délecter','délecte','merveilleuse','délicieuse',
          'émerveiller','émerveille','louer','loue','jubiler','jubile','merveille','suffisant','validé','validée','harmonieuse',
          'merveilleux','justice','perfection','délice','harmonie','beauté','bonté','efficace','grâce','intélligente']
#find_words
def test_find_words():
    assert find_words('')==[]
    assert find_words
    ('Cette phrase, est un test pour la 5467fonction find_words.')==['cette', 'phrase', 'est', 'un', 'test', 'pour', 'la', 'fonction','find_words']
    assert find_words('?.498248/')==[]
    assert find_words('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')==['AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'.lower()]
    assert find_words('6152 71278 17/03 6669420 ')==[]
    assert find_words('right-bicep for the win')==['right-bicep', 'for', 'the', 'win']
    try:
        assert find_words(['azez'])==[] 
    except:
        TypeError
    try:
        assert find_words(2)==[] 
    except:
        TypeError

#analyse
def test_analyse():
    assert analyse('merveilleux',[],[])==0
    assert analyse('6152 71278 17/03 6669420 ',POSITIF,NEGATIF)==0
    assert analyse('merveilleux',[],NEGATIF)==0
    assert analyse('merveilleux',POSITIF,[])==1
    assert analyse('je ne suis pas?',[],[])==0
    assert analyse('',[],[])==0
    assert analyse('insuffisant',POSITIF,NEGATIF)==-1
    assert analyse('suffisant',POSITIF,NEGATIF)==1
    assert analyse('la nature est belle beau merveilleux dégoûtant right bicep',POSITIF,NEGATIF)==0
    assert analyse('',POSITIF,NEGATIF)==0
    assert analyse('insuffisant',NEGATIF,POSITIF)==1
    try:
        analyse(['merveilleux'],POSITIF,NEGATIF)==1 
    except:
        TypeError
    try:
        analyse(2,POSITIF,NEGATIF)==1  
    except:
        TypeError

#avis
def test_avis():
    assert avis('',POSITIF,NEGATIF)==0
    assert avis('6152 71278 17/03 6669420 ',POSITIF,NEGATIF)==0
    assert avis('parfaits',POSITIF,NEGATIF)==1
    assert avis('parfait',POSITIF,NEGATIF)==1
    assert avis('parfait',POSITIF,NEGATIF)==analyse('parfait',POSITIF,NEGATIF)
    assert avis
    ("""je crois que cette solution est efficace car on ne peut prévoir les retards""",POSITIF,NEGATIF)==1
    assert avis
    ("""je crois que cette solution n'est pas efficace car on ne peut pas prévoir les retards""",POSITIF,NEGATIF)==-3
    #efficace+prévoir+retards
    assert avis("pas bien",POSITIF,NEGATIF)==-1
    assert avis("merveilleux bien",POSITIF,NEGATIF)==2
    assert avis("bla bla",POSITIF,NEGATIF)==0
    try:
        avis(['merveilleux'],POSITIF,NEGATIF)==1 
    except:
        TypeError
    try:
        avis(2,POSITIF,NEGATIF)==1  
    except:
        TypeError
    assert avis("""je valide cette idée, Malgré les "retards" """,POSITIF,NEGATIF)==0
#avis_commentaire
def test_avis_commentaire():
    assert avis_commentaire
    ("""je crois que cette solution est efficace car on ne peut prévoir les retards""")==1
    assert avis_commentaire
    ("""je crois que cette solution n'est pas efficace car on ne peut pas prévoir les retards""")==-1
    #pas efficace+ pas prévoir+retards
    assert avis_commentaire("""je valide cette idée, Malgré les "retards" """)==0
    #valide-retards

