Architecture — Data Migration Platform

Document de référence technique décrivant les choix d'architecture, les flux de données et les décisions de conception.

Table des matières :
1. Vue d'ensemble
2. Flux de données détaillé
3. Composants détaillés
4. Sécurité
5. Scalabilité
6. Résilience
7. Décisions d'architecture

1. Vue d'ensemble :
                                              DATA MIGRATION PLATFORM                              
                                                              │
    INGESTION                                 TRAITEMENT                          STOCKAGE          
    ─────────                                 ──────────                          ────────          
---------------                            ------------------               ----------------------------------        
   ADF                                       Blob Storage                              Azure Container    
   Pipeline             =====>                  raw/                                       Apps       
   02h UTC                                 -------------------                      
--------------                                      |                               --------------------                
                                                    v                                   Worker ETL   
                                           ----------------------                       KEDA 0->5 
                                              Event Grid                             ---------------------                                                                           
                                              BlobCreated                                    |
                                           -----------------------                           v               
                                                    |                                ------------------------   
                                                    v                                     DLQ Monitor
                                           ----------------------                         Prometheus 
                                               Service Bus                  |        -------------------------                             
                                               etl-topic                ==> |                    |
                                            ---------------------           |                    v
                                                                                      ----------------------------                                   
                                                                                            Azure SQL Database
                                                                                            customers          
                                                                                            processed_files 
                                                                                       ----------------------------
                                                                              ----------------------------------------------
OBSERVABILITE :                                                                                                 
   ------------------------------------------------------------------------------------------------------------------------
                           Azure Monitor | Log Analytics | Alertes | Dashboard  
   ------------------------------------------------------------------------------------------------------------------------

     INFRASTRUCTURE AS CODE                         CI/CD                           
     ──────────────────────                         ─────                           
  Terraform 1.15                                    GitHub Actions (4 jobs)         
  Backend: Azure Blob Storage                       test -> build -> deploy -> tf      
-------------------------------------------------------------------------------------------------------------------------------
2. Flux de données détaillé :
Pipeline nominal (le chemin heureux)
                                                                        
  2.1 ADF Pipeline (02h00 UTC)                                            
  ─────────────────────────                                              
  Azure SQL (customers)                                                  
         SELECT id, name, email, signup_date, country                   
         FROM customers                                                 
                    ▼                                                                 
  Blob Storage (raw/customers_legacy.csv)                                
                                                                         
  2.2. Event Grid (BlobCreated)                                            
  ──────────────────────────                                            
  Blob Storage -> Event Grid -> Service Bus (etl-topic/etl-sub)       
                                                                        
  2.3. KEDA Scale Up                                                       
  ────────────                                                        
  messageCount=1   -> 1 replica                                          
  messageCount=20  -> 1 replica                                        
  messageCount=40  -> 2 replicas                                       
  messageCount=100 -> 5 replicas (max)                              
                                                                         
  2.4. Worker ETL                                                    
  ─────────────                                           
                       
  Service Bus -> Worker                                                                                                    
                     1. Idempotence check                             
                          SELECT COUNT(*) FROM processed_files          
                          WHERE file_id = hash(blob_url)               
                          Si COUNT > 0 => SKIP (déjà traité)            
                                                                      
                     2. Extract                                       
                          BlobClient.download_blob()                    
                          pd.read_csv(BytesIO(data))                    
                                                                        
                     3. Transform                                     
                          - Normalisation colonnes (strip, lower)       
                          - Déduplication                               
                          - Validation email (regex)                    
                          - Standardisation country (FR, DE, BE...)     
                          - Gestion NULL (name => INCONNU)              
                          - Parse signup_date                           
                                                                        
                     4. Load                                          
                          df.to_sql("customers", engine, append)        
                          INSERT INTO processed_files(file_id, blob_url)
                                                                        
                     5. Complete message                              
                           receiver.complete_message(msg)               
   
Pipeline d'erreur (DLQ Path) :
                                                                       
  ValidationError (blob_url invalide, email manquant...) :                 
  ──────────────────────────────────────────────────────                 
  Worker -> dead_letter_message(reason="ValidationError")                                                        
                    |
                    v                                                    
  Service Bus DLQ -> DLQ Monitor  
                               - Log: reason + error_description + body           
                               - Prometheus: dlq_messages_total.inc()             
                               - Complete message (nettoyage DLQ)
     
  Exception temporaire (SQL timeout, Blob indisponible...) : 
------------------------------------------------------------             
  Worker -> abandon_message(msg)  # retry automatique                  
                                                                         
  delivery_count >= 10                                                   
  ────────────────────                                                   
  Worker -> dead_letter_message(reason="MaxRetriesExceeded")            
                                                                         
  Azure Monitor                                                          
  ─────────────                                                          
  DLQ > 0 -> Alerte -> Email admin
                 
3. Composants détaillés :
     Worker ETL (src/worker/main.py)
     ────────────────────  
            WORKER ETL                       
     Démarrage :                                         
     ──────────                                         
  while True:   # boucle de reconnexion               
      ServiceBusClient(                                
        transport=AmqpOverWebsocket,      # port 443       
        keep_alive=30                     # ping 30s        
     )                                                
    receiver(                                        
      max_wait_time=30,                              
      receive_mode=PEEK_LOCK                         
    )                                                
                                                     
  Réception  :                                        
  ──────────                                         
  for message in receiver:                           
    try:                                             
        process_message(msg)                           
    except ValidationError:                          
        safe_dead_letter(...)       # timeout 10s           
    except Exception:                                
        if delivery_count >= 10:                       
            safe_dead_letter(...)                        
        else:                                          
            abandon_message(...)    # retry               
        else:                                            
            safe_complete(...)           # succès                  
                                                    
Transform (src/core/transform.py) :
────────────────────--------------
                  TRANSFORM                         
                                                     
  Input: pd.DataFrame (CSV brut)                     
                                                     
  Étapes:                                          
  1. Normalisation colonnes                          
     col.strip().lower()                             
                                                     
  2. Déduplication                                   
     df.drop_duplicates()                            
                                                     
  3. Validation email                                
     regex: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
     Rejet des emails invalides                      
                                                     
  4. Standardisation country                        
     FRANCE -> FR                                     
     ALLEMAGNE -> DE                                 
     BELGIQUE -> BE  etc.                             
                                                     
  5. Gestion NULL                                    
     name=NULL -> INCONNU                             
     signup_date=NULL -> now()                        
     country=NULL -> UNKNOWN                          
                                                     
  Output: pd.DataFrame (données propres)             
   
Idempotence (src/core/idempotency.py) :
────────────────────────---------------
                  IDEMPOTENCE          
              
   file_id = SHA256(blob_url)                         
   already_processed(engine, file_id):                
    SELECT COUNT(*) FROM processed_files             
    WHERE file_id = :file_id                         
    -> True si COUNT > 0 (skip)                       
    -> False si COUNT = 0 (traiter)                                                                   
  Après traitement réussi:                           
    INSERT INTO processed_files                      
    (file_id, blob_url) VALUES (...)                                                                      
  Garantie: même fichier déposé N fois               
  -> traité exactement 1 fois       


              4. SÉCURITÉ                                 
 
Managed Identities (Zero Secret)                               
───────────────────────---------                              
  Worker Container App                                          
    - AcrPull -> ACR (pull images)                             
    - Azure Service Bus Data Receiver -> Service Bus            
    - Storage Blob Data Reader -> Blob Storage                  
    - SQL: CREATE USER FROM EXTERNAL PROVIDER                  
                                                                 
  ADF Pipeline                                                   
    - Storage Blob Data Contributor -> Blob Storage             
    - SQL DB Contributor -> SQL Server                          
                                                                 
  DLQ Monitor                                                    
    - AcrPull -> ACR                                            
    - Azure Service Bus Data Receiver -> Service Bus            
                                                                 
  Authentification SQL :                                           
  ─────────────────────                                         
  Token Azure AD (OAuth2)                                        
  struct.pack("<I{N}s", len(token_bytes), token_bytes)           
  cparams["attrs_before"] = {1256: token_struct}                 
  -> Pas de mot de passe SQL en clair       
                                                                                    
  Secrets CI/CD :                                                  
  ──────────---─                                                 
  GitHub Secrets (chiffrés)                                      
  terraform.tfvars (jamais commité -> .gitignore)                 

                       5. SCALABILITÉ                                                                                                
  
KEDA (Kubernetes Event-Driven Autoscaling)                     
──────────────────────────────────────────                                                                                      
  Trigger: azure-servicebus
                                      
 messageCount  │  replicas                                    
------------───────────────────────                                    
   0          ->    0   # scale to zero                        
   1 - 20     ->    1                                         
  21 - 40    ->    2                                         
  41 - 60    ->    3                                         
  61 - 80    ->    4                                         
  81 - 100  ->    5   # max replicas     

Paramètres:                                                    
    pollingInterval: 30s      # fréquence de vérification           
    cooldownPeriod: 300s  #  attente avant scale down            
    messageCount: 20       # seuil par replica                   
                                                                 
  Worker: 1 CPU / 2Gi RAM par replica                            
  DLQ Monitor: 0.5 CPU / 1Gi RAM (toujours 1 replica)           

                        6. RÉSILIENCE                                                                                                
  
Retry automatique (Service Bus)                                
────────────────────────────────                               
  max_delivery_count = 10                                        
  lock_duration = PT5M                                           
  abandon_message() -> retry après expiration du lock             
                                                                 
Reconnexion automatique (Worker)                               
─────────────────────────────────                              
  while True:                                                    
    try: connect + receive                                       
    except: sleep(5) + reconnect                                 
                                                                 
Transport WebSocket (port 443)                                 
─────────────────────────────                                  
  AmqpOverWebsocket -> contourne les firewalls                    
  keep_alive=30  -> maintient la connexion active                  
                                                                 
Settlement avec timeout                                        
─────────────────────────                                      
  safe_dead_letter(timeout=10s)                                  
  safe_complete(timeout=10s)                                     
  -> Si timeout: abandon_message() (retry)                        
                                                                 
Idempotence                                                    
───────────                                                    
  SHA256(blob_url) -> processed_files                             
  -> Garantie exactly-once processing                             

7. Décisions d'architecture :

a) Pourquoi j'ai préféré Azure Service Bus et non Azure Storage Queue ?
Parce que j’avais besoin d’un système capable de gérer un modèle pub/sub avec des topics et des subscriptions, ce que Storage Queue ne permet pas.
Service Bus m’a aussi offert une Dead Letter Queue native, ce qui était essentiel pour gérer les erreurs sans bloquer le pipeline.

En termes de scalabilité, les deux solutions sont compatibles avec KEDA, donc ce n’était pas un facteur différenciant.
En revanche, Service Bus propose une taille de message plus élevée et surtout la gestion de l’ordre via les sessions, ce qui est un avantage dans certains cas.

Donc au final, j’ai retenu Service Bus parce qu’il répond mieux aux besoins d’une architecture distribuée, résiliente et orientée événements.

b) Pourquoi Container Apps et non AKS ?
Critère	                   Container Apps	         AKS

KEDA intégré	              Natif	                Manuel
Scale to zero	              Natif	                Manuel
Gestion cluster	              Managé	                à gérer
Coût	                      Pay-per-use	        Cluster fixe
Complexité	              Faible	                Élevée
Choix                         Retenu	                Non

c) Pourquoi Managed Identity et non Connection String ?
Critère	             Managed Identity	     Connection String

Rotation secrets	 Automatique	          Manuelle
Secrets en clair	 Aucun	                  Dans le code
Audit Azure AD	         Complet	          Limité
Complexité	         Moyenne	          Simple
Choix	                 Retenu	                  Non

d) Pourquoi AMQP over WebSocket et non AMQP natif ?
Critère	               WebSocket (443)	          AMQP (5671)

Passage firewall	 Toujours ouvert	     Souvent bloqué
Performance	         Légèrement moindre	     Optimal
keep_alive	         Supporté	             Supporté
Choix	                 Retenu	                     Non

e) Pourquoi GitHub Actions et non Azure DevOps Pipelines ?
Critère	                 GitHub Actions	           Azure DevOps

Intégration GitHub	    Native	              Connexion OAuth
Coût	                    2000 min/mois gratuit     Gratuit aussi
Complexité setup	    Simple	              Complexe
Secrets management	    GitHub Secrets	      Variable groups
Choix	                    Retenu	              Non

8. Stack technique complète :

LANGAGE                       Python 3.12
FRAMEWORK ETL                 pandas, sqlalchemy, azure-servicebus, azure-storage-blob
AUTHENTIFICATION              azure-identity (DefaultAzureCredential)
BASE DE DONNÉES               Azure SQL (mssql+pyodbc, ODBC Driver 18)
MESSAGING                     Azure Service Bus (Standard, AmqpOverWebsocket)
CONTENEURS                    Docker -> Azure Container Registry -> Azure Container Apps
SCALING                       KEDA (azure-servicebus trigger)
STOCKAGE                      Azure Blob Storage (raw/, clean/)
ORCHESTRATION                 Azure Data Factory (Copy Activity, Trigger Schedule)
ÉVÉNEMENTS                    Azure Event Grid (BlobCreated -> Service Bus)
MONITORING                    Azure Monitor, Log Analytics, Prometheus
IaC                           Terraform 1.15 (provider azurerm 3.117)
CI/CD                         GitHub Actions (4 jobs: test, build, deploy, terraform)
STATE TERRAFORM               Azure Blob Storage (remote backend)
