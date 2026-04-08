# API Estudiantes — DynamoDB Local

API REST desarrollada con Django y Django REST Framework para la gestión de estudiantes y notas académicas. Utiliza DynamoDB Local como base de datos no relacional, Redis como caché y Docker para orquestar los servicios.

**Proyecto:** Bases de Datos No Relacionales  
**Integrantes:** Anuarth Rincón, Camilo Álvarez, Danilo Díaz, Juan Narváez, Victor Jaimes

---

## Stack tecnológico

| Tecnología | Uso |
|---|---|
| Django + DRF | Framework web y construcción de la API REST |
| boto3 | Cliente Python para DynamoDB Local |
| Redis | Caché con patrón cache-aside |
| gunicorn | Servidor WSGI en producción |
| Docker Compose | Orquestación de servicios |

---

## Estructura del proyecto

```
api-estudiantes-dynamodb/
├── docker-compose.yml        # Orquesta DynamoDB Local, Redis y la API
├── Dockerfile                # Imagen de la API (Python 3.12)
├── requirements.txt          # Dependencias Python
├── .env.example              # Variables de entorno documentadas
│
├── scripts/
│   ├── create_table.py       # Crea la tabla en DynamoDB Local
│   └── seed_data.py          # Inserta datos de prueba
│
└── app/
    ├── manage.py
    ├── config.py             # Fábrica de clientes DynamoDB y Redis
    ├── core/
    │   ├── settings.py       # Configuración Django (sin ORM ni migraciones)
    │   ├── urls.py           # Enrutamiento principal
    │   ├── views.py          # Endpoint /health
    │   └── wsgi.py
    ├── estudiantes/
    │   ├── repository.py     # Operaciones DynamoDB (CRUD de perfiles)
    │   ├── services.py       # Lógica de caché Redis (cache-aside)
    │   ├── serializers.py    # Validación de entrada y salida
    │   ├── views.py          # APIView para los endpoints
    │   └── urls.py
    └── notas/
        ├── repository.py     # Operaciones DynamoDB (CRUD de notas)
        ├── serializers.py
        ├── views.py
        └── urls.py
```

---

## Esquema DynamoDB — Single Table Design

Toda la información de estudiantes y notas se almacena en una sola tabla llamada `estudiantes`, usando una clave compuesta `pk` (partition key) + `sk` (sort key) para diferenciar los tipos de item.

| pk | sk | Atributos adicionales | Tipo de item |
|---|---|---|---|
| `EST#001` | `PERFIL` | `nombre_completo`, `correo_institucional` | Perfil del estudiante |
| `EST#001` | `NOTA#ALG_101` | `materia_nombre`, `nota` (Number) | Nota de una materia |
| `EST#002` | `PERFIL` | `nombre_completo`, `correo_institucional` | Perfil del estudiante |
| `EST#002` | `NOTA#BD_202` | `materia_nombre`, `nota` (Number) | Nota de una materia |

### Cómo se consultan los datos

**Obtener el perfil de un estudiante** — `GetItem` con clave exacta:
```
pk = "EST#001"  →  sk = "PERFIL"
```

**Listar todas las notas de un estudiante** — `Query` con `begins_with`:
```
pk = "EST#001"  →  sk begins_with "NOTA#"
```
Esto retorna todas las notas del estudiante en una sola operación, sin necesidad de conocer los códigos de materia.

**Obtener una nota específica** — `GetItem` con clave exacta:
```
pk = "EST#001"  →  sk = "NOTA#ALG_101"
```

**Listar todos los estudiantes** — `Scan` con filtro:
```
sk = "PERFIL"
```
Recorre toda la tabla y retorna solo los items de perfil. Se usa `Scan` porque no hay un índice secundario sobre `sk`.

### Transformación de respuestas DynamoDB

DynamoDB devuelve los datos con descriptores de tipo propios:
```json
{ "pk": {"S": "EST#001"}, "nota": {"N": "9.5"} }
```

Se usa `boto3.dynamodb.types.TypeDeserializer` en cada `repository.py` para convertirlos a tipos Python nativos. Los números se convierten a `Decimal` por el deserializer, por lo que se aplica una función `_fix_decimals` adicional para convertirlos a `float` antes de serializar la respuesta JSON.

---

## Cómo ejecutar el proyecto

### Requisitos previos
- Docker Desktop
- AWS CLI (para verificar la conexión a DynamoDB Local)

### 1. Configurar variables de entorno
```bash
cp .env.example .env
```

### 2. Levantar los servicios
```bash
docker compose up --build -d
```
Esto levanta tres contenedores:
- `dynamodb-local` en el puerto `8000`
- `redis` en el puerto `6379`
- `api` en el puerto `8080`

### 3. Crear la tabla en DynamoDB Local
```bash
docker compose exec api python /scripts/create_table.py
```

### 4. (Opcional) Insertar datos de prueba
```bash
docker compose exec api python /scripts/seed_data.py
```

### 5. Verificar que todo funciona
```bash
curl http://localhost:8080/health/
# {"dynamodb": "ok", "redis": "ok"}
```

### Documentación interactiva (Swagger UI)
Abre en el navegador:
```
http://localhost:8080/api/docs/
```

---

## Endpoints

### Utilidades

#### `GET /health/`
Verifica la conexión a DynamoDB Local y Redis.

**Respuesta:**
```json
{ "dynamodb": "ok", "redis": "ok" }
```

---

### Estudiantes

#### `POST /estudiantes/`
Crea el perfil de un nuevo estudiante.

**Body:**
```json
{
  "id": "001",
  "nombre_completo": "Ana Torres",
  "correo_institucional": "ana.torres@uni.edu"
}
```

**Respuesta `201`:**
```json
{
  "pk": "EST#001",
  "sk": "PERFIL",
  "nombre_completo": "Ana Torres",
  "correo_institucional": "ana.torres@uni.edu"
}
```

---

#### `GET /estudiantes/`
Lista todos los estudiantes registrados (operación `Scan`).

**Respuesta `200`:**
```json
[
  {
    "pk": "EST#001",
    "sk": "PERFIL",
    "nombre_completo": "Ana Torres",
    "correo_institucional": "ana.torres@uni.edu"
  }
]
```

---

#### `GET /estudiantes/{id}/`
Obtiene el perfil de un estudiante. Implementa **caché Redis** (cache-aside): el primer request consulta DynamoDB y guarda el resultado en Redis con un TTL configurable; los requests siguientes se sirven desde Redis.

**Respuesta `200`:**
```json
{
  "pk": "EST#001",
  "sk": "PERFIL",
  "nombre_completo": "Ana Torres",
  "correo_institucional": "ana.torres@uni.edu"
}
```

**Respuesta `404`:**
```json
{ "error": "Estudiante no encontrado" }
```

---

#### `DELETE /estudiantes/{id}/`
Elimina el perfil de un estudiante e invalida su entrada en el caché Redis.

**Respuesta `204`:** sin cuerpo  
**Respuesta `404`:** `{ "error": "Estudiante no encontrado" }`

---

### Notas

#### `POST /notas/`
Agrega una nota a un estudiante existente.

**Body:**
```json
{
  "estudiante_id": "001",
  "codigo_materia": "ALG_101",
  "materia_nombre": "Algoritmos",
  "nota": 9.5
}
```

**Respuesta `201`:**
```json
{
  "pk": "EST#001",
  "sk": "NOTA#ALG_101",
  "materia_nombre": "Algoritmos",
  "nota": 9.5
}
```

---

#### `GET /estudiantes/{id}/notas/`
Lista todas las notas de un estudiante (operación `Query` con `begins_with(sk, "NOTA#")`).

**Respuesta `200`:**
```json
[
  { "pk": "EST#001", "sk": "NOTA#ALG_101", "materia_nombre": "Algoritmos", "nota": 9.5 },
  { "pk": "EST#001", "sk": "NOTA#BD_202", "materia_nombre": "Bases de Datos", "nota": 8.7 }
]
```

---

#### `GET /estudiantes/{id}/notas/{codigo}/`
Obtiene una nota específica de un estudiante.

**Respuesta `200`:**
```json
{
  "pk": "EST#001",
  "sk": "NOTA#ALG_101",
  "materia_nombre": "Algoritmos",
  "nota": 9.5
}
```

**Respuesta `404`:**
```json
{ "error": "Nota no encontrada" }
```

---

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django | — |
| `DEBUG` | Modo debug | `False` |
| `DYNAMODB_ENDPOINT` | URL de DynamoDB Local | `http://dynamodb-local:8000` |
| `DYNAMODB_TABLE` | Nombre de la tabla | `estudiantes` |
| `AWS_ACCESS_KEY_ID` | Credencial (cualquier valor para local) | `dummy` |
| `AWS_SECRET_ACCESS_KEY` | Credencial (cualquier valor para local) | `dummy` |
| `AWS_DEFAULT_REGION` | Región AWS | `us-east-1` |
| `REDIS_HOST` | Host de Redis | `redis` |
| `REDIS_PORT` | Puerto de Redis | `6379` |
| `CACHE_TTL` | Tiempo de vida del caché en segundos | `300` |
