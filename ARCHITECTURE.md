# Architettura uniCMS

## Panoramica

uniCMS è un Content Management System modulare costruito con Django Framework. Questo documento descrive l'architettura del sistema, i componenti principali e le loro interazioni.

## Struttura del Progetto

```
uniCMS/
├── src/cms/                    # Codice sorgente principale
│   ├── api/                    # API REST
│   ├── carousels/              # Gestione caroselli
│   ├── contacts/               # Gestione contatti
│   ├── contexts/               # Contesti e WebPath
│   ├── cookies_consent/        # Gestione consenso cookie
│   ├── medias/                 # Gestione media e file
│   ├── menus/                  # Gestione menu di navigazione
│   ├── pages/                  # Gestione pagine
│   ├── publications/           # Gestione pubblicazioni/articoli
│   ├── search/                 # Funzionalità di ricerca
│   └── templates/              # Template e blocchi
├── docs/                       # Documentazione
├── example/                    # Progetto di esempio
└── dumps/                      # Dump database di esempio
```

## Componenti Principali

### 1. Contexts (Contesti)

Il modulo `contexts` gestisce la struttura gerarchica dei siti web e i permessi editoriali.

#### WebSite
- **Scopo**: Rappresenta un sito web con dominio e lingua predefinita
- **Relazioni**: Contiene multipli WebPath
- **Caratteristiche**: Supporto multilingua, gestione permessi

#### WebPath
- **Scopo**: Definisce i percorsi/contesti del sito (es. /, /en/, /news/)
- **Struttura**: Gerarchica con parent-child relationships
- **Caratteristiche**:
  - Supporto alias e redirect
  - Gestione fullpath automatica
  - Meta tag SEO (description, keywords, robots)
  - Controllo accessi per gruppi utenti

#### EditorialBoardEditors
- **Scopo**: Gestisce i permessi degli utenti sui WebPath
- **Livelli di permesso**:
  - 0: Nessun permesso
  - 1: Visualizzazione
  - 2: Traduzione (con ereditarietà)
  - 3: Traduzione (solo contesto corrente)
  - 4: Modifica (con ereditarietà)
  - 5: Modifica (solo contesto corrente)
  - 6: Pubblicazione (con ereditarietà)
  - 7: Pubblicazione (solo contesto corrente)

#### Sistema di Lock
- **EditorialBoardLock**: Blocca oggetti per editing esclusivo
- **EditorialBoardLockUser**: Associa utenti autorizzati ai lock
- **Utilizzo**: Previene conflitti durante la modifica simultanea

### 2. Pages (Pagine)

Il modulo `pages` gestisce le pagine del sito e i loro elementi.

#### Page
- **Scopo**: Contenuto principale pubblicabile nel sito
- **Stati**: draft, published
- **Caratteristiche**:
  - Sistema di bozze (draft_of)
  - Date di pubblicazione (date_start, date_end)
  - Associazione a WebPath e PageTemplate
  - Supporto localizzazione
  - Tag e SEO

#### Elementi di Pagina
- **PageBlock**: Blocchi di contenuto nella pagina
- **PageCarousel**: Caroselli associati
- **PageContact**: Contatti visualizzati
- **PageMedia**: Media e immagini
- **PageMediaCollection**: Collezioni di media
- **PageMenu**: Menu di navigazione
- **PageLink**: Link esterni
- **PagePublication**: Pubblicazioni incluse
- **PageHeading**: Intestazioni con localizzazione

#### Sistema di Blocchi
I blocchi vengono aggregati da due fonti:
1. **PageBlock**: Blocchi specifici della pagina
2. **PageTemplateBlock**: Blocchi ereditati dal template

Il metodo `get_blocks()` combina entrambe le fonti con logica di override.

### 3. Publications (Pubblicazioni)

Il modulo `publications` gestisce contenuti editoriali come articoli e news.

#### Category
- **Scopo**: Organizzazione e classificazione delle pubblicazioni
- **Caratteristiche**: Nome, descrizione, immagine rappresentativa

#### Publication
- **Scopo**: Contenuto editoriale pubblicabile
- **Formati contenuto**: HTML, Markdown
- **Caratteristiche**:
  - Slug auto-generato
  - Tag e categorie
  - Immagini (preview e presentation)
  - Rilevanza per ordinamento
  - Note editoriali interne

#### PublicationContext
- **Scopo**: Associa pubblicazioni a WebPath specifici
- **Caratteristiche**:
  - Date di pubblicazione per contesto
  - Periodo di evidenza (in_evidence_start/end)
  - URL generato automaticamente
  - Ordinamento per webpath e data

#### Elementi di Pubblicazione
- **PublicationRelated**: Pubblicazioni correlate
- **PublicationLink**: Link esterni
- **PublicationBlock**: Blocchi di contenuto
- **PublicationMediaCollection**: Collezioni media
- **PublicationAttachment**: File allegati
- **PublicationLocalization**: Traduzioni

### 4. Templates

Il modulo `templates` fornisce l'infrastruttura per i template e blocchi riutilizzabili.

#### PageTemplate
- **Scopo**: Template base per le pagine
- **Caratteristiche**: Definisce layout e blocchi predefiniti

#### TemplateBlock
- **Scopo**: Blocchi di contenuto riutilizzabili
- **Tipi**: Diversi tipi di blocchi (HTML, Placeholder, etc.)

### 5. API

Il modulo `api` fornisce un'interfaccia REST compliant con OpenAPI v3.

**Caratteristiche**:
- Serializzazione automatica
- Paginazione
- Filtri e ordinamento
- Gestione permessi
- Gestione concorrenza

### 6. Medias

Gestione centralizzata di file e media.

**Caratteristiche**:
- Validazione file (tipo, dimensione)
- Organizzazione in collezioni
- Metadati (titolo, descrizione, alt text)
- Path generati automaticamente

### 7. Menus

Gestione menu di navigazione.

**Caratteristiche**:
- Struttura gerarchica
- Link interni ed esterni
- Ordinamento personalizzabile

### 8. Carousels

Gestione slider e caroselli di immagini.

**Caratteristiche**:
- Slide multiple
- Ordinamento
- Associazione a pagine

## Pattern e Convenzioni

### Classi Astratte

#### ActivableModel
- Aggiunge campo `is_active` per soft-delete
- Permette disattivazione invece di eliminazione

#### TimeStampedModel
- Aggiunge `created` e `modified` timestamp
- Tracciamento automatico delle modifiche

#### CreatedModifiedBy
- Aggiunge `created_by` e `modified_by`
- Traccia chi ha creato/modificato l'oggetto

#### AbstractDraftable
- Sistema di bozze con `draft_of`
- Metodo `toggleState()` per pubblicazione

#### AbstractPublicable
- Verifica pubblicabilità con date
- Property `is_publicable`

#### AbstractLockable
- Supporto sistema di lock
- Metodo `is_lockable_by(user)`

### Sistema di Permessi

Il sistema di permessi è multi-livello:

1. **Superuser**: Accesso completo
2. **Django Permissions**: Permessi modello standard
3. **Editorial Board**: Permessi contestuali per WebPath
4. **Locks**: Permessi temporanei su oggetti specifici

Metodi standard per verifiche:
- `is_localizable_by(user)`: Può tradurre?
- `is_editable_by(user)`: Può modificare?
- `is_publicable_by(user)`: Può pubblicare?
- `is_lockable_by(user)`: Può bloccare?

### Caching

Il sistema utilizza caching aggressivo per performance:

- Attributi cached con prefisso `_` (es. `_blocks_`, `_pubs`)
- Metodo `clean_related_caches()` per invalidazione
- Cache basata su Redis con TTL

### Localizzazione

Supporto multilingua tramite modelli di localizzazione:
- `PageLocalization`
- `PublicationLocalization`
- `PageHeadingLocalization`

Metodo standard: `translate_as(lang)`

## Flusso di Lavoro Editoriale

### Creazione Contenuto

1. Utente crea bozza (state='draft')
2. Modifica e revisione
3. Pubblicazione (toggleState)
4. Bozza diventa pubblicata, vecchia versione disattivata

### Gestione Permessi

1. Verifica superuser
2. Verifica permessi Django
3. Verifica Editorial Board per WebPath
4. Verifica lock su oggetto
5. Verifica permessi ereditati da parent

### Pubblicazione Multi-Contesto

1. Pubblicazione creata
2. PublicationContext creati per ogni WebPath
3. Date di pubblicazione per contesto
4. URL generati automaticamente
5. Visibilità controllata da date e is_active

## Best Practices

### Sviluppo

1. **Usare classi astratte**: Eredita da ActivableModel, TimeStampedModel, etc.
2. **Implementare permessi**: Usa metodi is_*_by(user)
3. **Gestire cache**: Invalida cache quando necessario
4. **Validare input**: Usa validators Django
5. **Documentare**: Aggiungi docstring a classi e metodi

### Performance

1. **Select related**: Usa select_related() per foreign keys
2. **Prefetch related**: Usa prefetch_related() per many-to-many
3. **Cache query**: Salva risultati in attributi _cached
4. **Indici database**: Aggiungi indici per campi frequentemente cercati
5. **Paginazione**: Usa sempre paginazione per liste

### Sicurezza

1. **Validazione input**: Sempre validare dati utente
2. **Permessi**: Verifica permessi prima di ogni operazione
3. **Sanitizzazione**: Usa mark_safe solo quando necessario
4. **CSRF**: Usa token CSRF per form
5. **SQL Injection**: Usa sempre ORM Django

## Testing

### Struttura Test

```python
from django.test import TestCase

class ModelTestCase(TestCase):
    def setUp(self):
        # Setup test data
        pass
    
    def test_creation(self):
        # Test object creation
        pass
    
    def test_permissions(self):
        # Test permission methods
        pass
```

### Coverage

Eseguire test con coverage:
```bash
coverage run ./manage.py test cms
coverage report -m
```

## Deployment

### Requisiti

- Python 3.10+
- Django 4.x
- PostgreSQL/MySQL (produzione)
- Redis (caching)
- MongoDB (search - opzionale)

### Configurazione

1. Variabili ambiente
2. Database setup
3. Migrazioni
4. Collectstatic
5. Configurazione web server (nginx/apache)
6. Configurazione WSGI/ASGI

## Estensioni e Plugin

uniCMS supporta estensioni tramite:

1. **Django Apps**: Aggiungi app in INSTALLED_APPS
2. **Template Blocks**: Crea nuovi tipi di blocchi
3. **API Endpoints**: Estendi API REST
4. **Middleware**: Aggiungi middleware custom
5. **Signals**: Usa signals Django per hook

## Risorse

- [Documentazione ufficiale](https://unicms.readthedocs.io/)
- [Repository GitHub](https://github.com/UniversitaDellaCalabria/uniCMS)
- [Issue Tracker](https://github.com/UniversitaDellaCalabria/uniCMS/issues)
