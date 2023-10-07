from typing import List, NewType
def find_words(ch:str) -> List[str]:
    """Fonction qui permet de prendre une chaine de caractères
        comme paramétre et retourne une liste de caractères
        dont ses éléments sont les mots de la chaine en les mettant
        en miniscule"""
    l=[]
    word=''
    for i in range(len(ch)):
        word+=ch[i]
        if ch[i] in [' ','"',',',';','?','.',':','/','~','#','{','[','|','...','(',')',']','«','»'] or ch[i] in [str(k) for k in range(10)]:
            l.append(word[:len(word)-1])
            word=''
    l.append(word.lower())
    l1=[]
    for k in range(len(l)):
        if l[k]!='':
            l1.append(str(l[k]).lower())     
    return(l1)

#C'est une fonction de complexité linéaire



def analyse(word:str,positif:List[str],NEGATIF:List[str])->-1|0|1:
    """fonction qui permet de voir si un mot
        est positif ou négatif"""
    if word in positif or word[:len(word)-1] in positif:
        return(1)
    elif word in NEGATIF or word[:len(word)-1] in NEGATIF:
        return(-1)
    elif len(word)>=6:
        a=word[-3:len(word)]=='ard' or word[-4:len(word)-1]=='ard' or word[-4:len(word)]=='asse' or word[-5:len(word)-1]=='asse'
        b=word[-4:len(word)]=='âtre' or word[-5:len(word)-1]=='âtre' or word[-5:len(word)]=='aille' or word[-6:len(word)-1]=='aille'
        c=word[-3:len(word)]=='aud' or word[-4:len(word)-1]=='aud' or word[-5:len(word)]=='asser'
        d=word[-4:len(word)]=='oter' or word[-5:len(word)-1]=='oter' or word[-6:len(word)]=='ailler' or word[-7:len(word)-1]=='ailler'
        a=a or b or c or d
        if  a:
            return(-1)
        if  word[-6:len(word)]=='issime' or word[-7:len(word)-1]=='issime' or word[0:5]=='archi' or word[1:6]=='archi' or word[0:5]=='extra' or word[1:6]=='extra':
            return(1)
        else:
            return(0)
    else:
        return(0)

NEGATIF=['nul', 'nulle', 'détestable','horrible','laid','laide','méchant','affreux','idiot','débile','déception','tromper','insuffisante','invalidée',
          'stupide','ridicule','raté','médiocre','ennuyeux','pitoyable','effrayant','trompe','invalide','méchante','ratée','haïr','déçue',
          'dégoûtant','dégoûtante','mauvais','mauvaise','imbécile','déteste','hais','scandaliser','déçu','insuffisant','invalidé','affreuse','effrayante',
          'moque','dégoûte','effraie','effraye','ennuie','indigne','déçoit','injuste','imperfection','inefficace','ennuyeuse']

POSITIF=['génie','beau', 'belle', 'merveilleux','superbe', 'bien', 'bon', 'bonne', 'aimant','enthousiasmant','aimable','valide','prévoir',
          'distrayant','juste','aimable','réussi','reussie','parfait','délicieux','harmonieux','intélligent','prévois','aimante',
          'intélligence','apprécier','approuver','approuve','adorer','adore','délecter','délecte','merveilleuse','délicieuse',
          'émerveiller','émerveille','louer','loue','jubiler','jubile','merveille','suffisant','validé','validée','harmonieuse',
          'merveilleux','justice','perfection','délice','harmonie','beauté','bonté','efficace','grâce','intélligente']



def avis(comment:str,positif:List[str],negatif:List[str])->int:
    """Cette fonction retourne si un commentaire
        est positif ou négatif"""
    l=find_words(comment)
    s=0
    if len(l)>2:
        if l[0] in ['pas','non','jamais','plus','point','guère','aucun','nullement']:
            s=-1*analyse(l[1],positif,negatif)
        else:
            s=analyse(l[0],positif,negatif)+analyse(l[1],positif,negatif)
        for i in range(2,len(l)):
            if l[i-1] in ['pas','non','jamais','plus','point','guère','aucun','nullement'] or l[i][0]=='"' or l[i-2] in ['non','pas','jamais','plus','point','guère','aucun','nullement']:
                s-=analyse(l[i],positif,negatif)
            else:
                s+=analyse(l[i],positif,negatif)
    elif len(l)==2:
        if l[0] in ['pas','non','jamais','plus','point','guère','aucun','nullement']:
            return -1*analyse(l[1],positif,negatif)
        else:
            for i in range(2):
                s+=analyse(l[i],positif,negatif)
    elif len(l)>0:
        s=analyse(l[0],positif,negatif)
    
    else:
        s=0
    return s

#la fonction avis renvoie un entier. S'il est positif alors c'est un avis positif,
# si c'est 0 c'est un avis neutre et si c'est négatif c'est un avis négatif
def avis_commentaire(comment:str):
    a = avis(comment, POSITIF, NEGATIF)
    return 1 if a>0 else -1 if a<0 else 0 
#toutes ces fonctions sont de compléxités linéaires
