```mermaid
flowchart TD
    Start[Book ID cible] --> Verif{Livre cible<br/>dans BOOKS ?}
    
    Verif -->|Non| DownloadRef[Télécharger livre cible]
    Verif -->|Oui| LoadRef[Charger depuis cache]
    
    DownloadRef --> CacheRef[Sauvegarder cache<br/>ID.txt]
    CacheRef --> LoadRef
    
    LoadRef --> DownloadAll[Télécharger 21 livres<br/>de référence]
    
    DownloadAll --> CacheAll[Sauvegarder tous les caches]
    
    CacheAll --> Nettoyer[Nettoyer tous les textes]
    
    Nettoyer --> Vectoriser[TF-IDF Vectorization<br/>max_features=1000<br/>stop_words=english]
    
    Vectoriser --> Matrice[Créer matrice<br/>documents × termes]
    
    Matrice --> Index{Trouver index<br/>du livre cible}
    
    Index --> Cosinus[Similarité Cosinus<br/>Target vs Tous]
    
    Cosinus --> Scores[Vector de scores<br/>de similarité]
    
    Scores --> Trier[Trier décroissant<br/>argsort::-1]
    
    Trier --> Exclure{Exclure<br/>livre cible ?}
    
    Exclure -->|idx == target| Ignorer[Ignorer ce score]
    Exclure -->|idx != target| Ajouter[Ajouter au résultat]
    
    Ajouter --> Compter{5 livres<br/>trouvés ?}
    
    Compter -->|Non| Suivant[Prendre suivant]
    Compter -->|Oui| Titres[Récupérer titres<br/>depuis BOOKS dict]
    
    Suivant --> Ajouter
    
    Titres --> Liste[Construire liste<br/>5 titres]
    
    Liste --> Retour["Renvoyer list[str]<br/>titres triés"]
    ```
