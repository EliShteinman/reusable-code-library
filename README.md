# ספריית קוד משותף - מבנה מוצע

## reusable-code-library/

### 1. fastapi-templates/
```
fastapi-templates/
├── basic-structure/
│   ├── main.py                 # תבנית FastAPI בסיסית עם lifespan
│   ├── models.py               # תבניות Pydantic בסיסיות
│   └── __init__.py
├── database-integration/
│   ├── mysql-dal.py            # DataLoader עם Connection Pool
│   ├── mongodb-dal.py          # DataLoader למונגו (עתידי)
│   └── dependencies.py        # Dependency injection pattern
└── crud-operations/
    ├── items_router.py         # CRUD router מלא
    └── health_checks.py        # Health check endpoints
```

### 2. kubernetes-templates/
```
kubernetes-templates/
├── databases/
│   ├── mysql/
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── pvc.yaml
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── mongodb/
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── pvc.yaml
│       ├── deployment.yaml
│       └── service.yaml
├── applications/
│   ├── fastapi-deployment.yaml
│   ├── fastapi-service.yaml
│   └── route.yaml
└── common/
    ├── namespace.yaml
    └── labels-template.yaml
```

### 3. scripts-library/
```
scripts-library/
├── openshift/
│   ├── deployment-commands.bat
│   ├── deployment-commands.sh
│   ├── cleanup-commands.bat
│   └── cleanup-commands.sh
├── docker/
│   ├── build-and-push.bat
│   ├── build-and-push.sh
│   └── Dockerfile-templates/
└── database/
    ├── mysql/
    │   ├── create_basic_table.sql
    │   └── insert_sample_data.sql
    └── mongodb/
        └── init_collections.js
```

### 4. configuration-templates/
```
configuration-templates/
├── requirements/
│   ├── fastapi-mysql.txt
│   ├── fastapi-mongodb.txt
│   └── basic-fastapi.txt
├── environment/
│   ├── .env-template
│   └── docker-compose.yml-template
└── gitignore/
    └── python-docker.gitignore
```

### 5. quick-reference/
```
quick-reference/
├── openshift-commands.md       # פקודות נפוצות
├── kubectl-cheatsheet.md       # פקודות k8s
├── docker-commands.md          # פקודות Docker
├── troubleshooting.md          # בעיות נפוצות ופתרונות
└── exam-checklist.md           # רשימת בדיקה למבחן
```