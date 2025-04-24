# Šablona projektu pro vývoj IS

Tato šablona slouží jako výchozí bod pro vývoj informačního systému v rámci předmětu Vývoj IS. Poskytuje základní strukturu a konfiguraci pro moderní webovou aplikaci s odděleným backendem a frontendem, využívající kontejnerizaci pomocí Dockeru.

## Použité technologie

* **Backend:**
    * Python 3.10+
    * FastAPI: Moderní, rychlý webový framework pro tvorbu API.
    * SQLAlchemy: ORM (Object-Relational Mapper) pro práci s databází.
    * Alembic: Nástroj pro správu databázových migrací (sledování změn schématu).
    * Pydantic: Validace dat a serializace (používá FastAPI).
    * Uvicorn: ASGI server pro běh FastAPI.
* **Frontend:**
    * React: JavaScriptová knihovna pro tvorbu uživatelských rozhraní (základní nastavení).
    * Node.js: Prostředí pro běh JavaScriptu a správu frontendových závislostí (npm).
* **Databáze:**
    * PostgreSQL: Výkonná open-source relační databáze.
* **Kontejnerizace:**
    * Docker & Docker Compose: Pro vytvoření izolovaných, přenositelných a snadno spravovatelných prostředí pro jednotlivé části aplikace (backend, frontend, databáze).

## Struktura projektu

```bash
vyvoj-IS-sablona/
├── backend/                 # Adresář pro backend (FastAPI)
│   ├── app/                 # Hlavní kód aplikace
│   │   ├── init.py
│   │   ├── main.py          # Vstupní bod FastAPI aplikace
│   │   ├── core/            # Konfigurace, nastavení
│   │   ├── db/              # Databázová vrstva (session, base model)
│   │   ├── models/          # SQLAlchemy modely
│   │   ├── schemas/         # Pydantic schémata (API modely)
│   │   └── api/             # API endpointy (routry)
│   ├── alembic/             # Adresář pro Alembic migrace
│   │   ├── versions/        # Vygenerované migrační skripty
│   │   ├── env.py           # Konfigurace Alembic prostředí
│   │   └── script.py.mako # Šablona pro migrační skripty
│   ├── alembic.ini          # Hlavní konfigurace Alembicu
│   ├── requirements.txt     # Python závislosti
│   ├── Dockerfile           # Dockerfile pro backend
│   └── .env                 # Proměnné prostředí (lokální, nekómitovat!)
├── frontend/                # Adresář pro frontend (React)
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── Dockerfile           # Dockerfile pro frontend (vývojový)
├── docker-compose.yml       # Konfigurace Docker Compose pro spuštění všech služeb
└── README.md                # Tento soubor
## Nastavení a spuštění
```

1.  **Nainstalujte Docker a Docker Compose.**
2.  **Vytvořte soubor `backend/.env`:** V adresáři `backend` vytvořte soubor `.env` a nastavte v něm proměnné pro připojení k databázi. Můžete zkopírovat a upravit `backend/.env.example` (pokud bude vytvořen). Minimálně by měl obsahovat:
    ```ini
    POSTGRES_USER=template_user
    POSTGRES_PASSWORD=template_password # Zvolte silné heslo!
    POSTGRES_DB=template_db
    POSTGRES_SERVER=db # Název služby DB v docker-compose
    POSTGRES_PORT=5432

    # URL pro SQLAlchemy a Alembic (automaticky sestaveno nebo zadáno přímo)
    DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}

    # Další nastavení (např. secret key pro JWT)
    # SECRET_KEY=vas_velmi_tajny_klic
    ```
3.  **Sestavení a spuštění kontejnerů:** V kořenovém adresáři projektu spusťte:
    ```bash
    docker-compose up --build -d
    ```
4.  **Databázové migrace (Alembic):** Při prvním spuštění nebo po změně modelů je potřeba vytvořit a aplikovat migrace. Připojte se do běžícího backend kontejneru a spusťte příkazy Alembicu:
    ```bash
    # Připojení do kontejneru (pokud běží)
    docker-compose exec backend bash

    # Uvnitř kontejneru:
    # Vygenerování nové migrace (pokud jste změnili modely v backend/app/models/)
    alembic revision --autogenerate -m "Popis vaší změny modelů"

    # Aplikování migrací na databázi
    alembic upgrade head

    # Odpojení od kontejneru
    exit
    ```
    *Alternativně lze spouštění migrací integrovat do `command` v `docker-compose.yml`.*

5.  **Přístup k aplikaci:**
    * **Backend API:** [http://localhost:8000](http://localhost:8000)
    * **Interaktivní API dokumentace (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
    * **Alternativní API dokumentace (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
    * **Frontend (React Dev Server):** [http://localhost:3000](http://localhost:3000)
    * **Databáze (např. přes DBeaver/pgAdmin):** Host: `localhost`, Port: `5434`, Databáze: `template_db`, Uživatel: `template_user`, Heslo: (vaše heslo z `.env`)

## Další kroky

Tato šablona poskytuje základ. Další kroky zahrnují:

1.  Definování vlastních SQLAlchemy modelů v `backend/app/models/`.
2.  Definování odpovídajících Pydantic schémat v `backend/app/schemas/`.
3.  Implementace API endpointů v `backend/app/api/`.
4.  Vytváření a aplikování databázových migrací pomocí Alembicu po každé změně modelů.
5.  Vývoj frontendové části v Reactu v adresáři `frontend/`.

---
Tato šablona by měla usnadnit start vývoje vašeho projektu v rámci kurzu.
