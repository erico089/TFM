# Sistema de Agentes Inteligentes

Este repositorio contiene el código para crear un sistema de ayudas inteligentes.  
Está compuesto por tres aplicaciones:

- Una **app de navegación**
- Una **app de crawling**
- Una **app de chat**

Estas aplicaciones trabajan conjuntamente para conformar el sistema completo de ayudas inteligentes.


## Tabla de Contenidos

- [Descripción general](#descripción-general)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración del entorno](#configuración-del-entorno)
- [Cómo ejecutar las aplicaciones](#cómo-ejecutar-las-aplicaciones)
- [Uso](#uso)
- [Tests](#tests)
- [Para acabar](#importante)


## Descripción general

El Sistema de Agentes Inteligentes está diseñado para automatizar la recolección de datos y permitir su consulta mediante lenguaje natural.

- Las primeras dos aplicaciones (**navegación** y **crawling**) se encargan de explorar y extraer datos de manera automática desde distintas fuentes.
- La tercera aplicación (**chat**) permite consultar los datos recopilados a través de un asistente conversacional, utilizando lenguaje natural.

Este enfoque facilita la interacción intuitiva con grandes volúmenes de información previamente recolectada y organizada.

## Estructura del repositorio

El repositorio se organiza principalmente en tres aplicaciones independientes:

```bash
/app_chat/        --> Aplicación de chat para consultas en lenguaje natural
/app_crawler/    --> Aplicación para extracción automática de datos (crawling)
/app_navigation/  --> Aplicación para navegación automática y exploración de fuentes
/data/           --> Carpeta generada automáticamente que almacena los datos extraídos
```

Además, existen otros archivos y carpetas auxiliares en la raíz del repositorio, como configuraciones, documentación y scripts de soporte.

## Requisitos previos

Para el correcto funcionamiento del sistema, se recomienda el uso de **Conda** para crear un entorno virtual independiente para cada una de las aplicaciones, ya que sus dependencias no son exactamente las mismas.

Requisitos principales:

- [Conda](https://docs.conda.io/en/latest/) (recomendado para la gestión de entornos)
- Python 3.11.11
- PostgreSQL (como sistema de base de datos)

Asegúrate de tener estas herramientas instaladas antes de continuar con la instalación del proyecto.

## Instalación

Sigue los siguientes pasos para instalar el proyecto en tu máquina local:

1. **Clona el repositorio:**

```bash
git clone https://github.com/usuario/tu-repo.git
cd tu-repo
```

2. **Instala una versión estable de PostgreSQL:**

- Descarga e instala PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/).
- Asegúrate de configurar correctamente un usuario, contraseña y base de datos.

3. **(Recomendado) Instala Conda para la gestión de entornos virtuales:**

- Descarga Miniconda o Anaconda desde [conda.io](https://docs.conda.io/en/latest/miniconda.html).
- Sigue las instrucciones de instalación según tu sistema operativo.

## Configuración del entorno

Una vez que hayas instalado Conda y PostgreSQL, sigue los siguientes pasos para configurar el entorno para cada una de las aplicaciones, todo desde la carpeta raíz del proyecto.

### 1. Crear y activar un entorno Conda para **AppChat**:

```bash
# Crea un entorno Conda con Python 3.11.11
conda create -n appchat_env python=3.11.11

# Activa el entorno
conda activate appchat_env

# Navega a la carpeta de la aplicación
cd app_chat

# Instala las dependencias desde requirements.txt
pip install -r requirements.txt
```

### 2. Crear y activar un entorno Conda para **AppCrawling**:

```bash
# Vuelve a la carpeta raíz del proyecto
cd ..

# Crea un entorno Conda con Python 3.11.11
conda create -n appcrawling_env python=3.11.11

# Activa el entorno
conda activate appcrawling_env

# Navega a la carpeta de la aplicación
cd app_crawler

# Instala las dependencias desde requirements.txt
pip install -r requirements.txt
```

### 3. Crear y activar un entorno Conda para **AppNavegacion**:

```bash
# Vuelve a la carpeta raíz del proyecto
cd ..

# Crea un entorno Conda con Python 3.11.11
conda create -n appnavegacion_env python=3.11.11

# Activa el entorno
conda activate appnavegacion_env

# Navega a la carpeta de la aplicación
cd app_navigation

# Instala las dependencias desde requirements.txt
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Dentro de la carpeta raíz del proyecto, encontrarás el archivo `.env.example`. Este archivo contiene varias variables de entorno que deben ser configuradas con las claves necesarias para que las aplicaciones funcionen correctamente.

**Pasos para configurar el `.env`:**

1. Copia el archivo `.env.example` y renómbralo a `.env`:

   ```bash
   cp .env.example .env
   ```

2. Abre el archivo `.env` y configura las siguientes variables:

   - **POSTGRES_USER**: El usuario de PostgreSQL que vas a utilizar.
   - **POSTGRES_PASSWORD**: La contraseña del usuario de PostgreSQL.
   - **AZURE_OPENAI_API_KEY**: La clave de API de Azure OpenAI para acceder al modelo.
   - **AZURE_DEPLOYMENT_NAME**: El nombre del despliegue del modelo en Azure.
   - **AZURE_OPENAI_INPUT**: El punto de entrada para interactuar con Azure OpenAI.
   - **AZURE_API_VERSION**: La versión de la API de Azure que vas a utilizar.
   - **AZURE_OPENAI_MODEL_ID**: El identificador del modelo en Azure OpenAI que se utilizará.
   - **AZURE_EMBEDDING_KEY**: La clave de API para embeddings en Azure.
   - **AZURE_EMBEDDING_DEPLOYMENT_NAME**: El nombre del despliegue del modelo de embeddings en Azure.
   - **AZURE_EMBEDDING_ENDPOINT**: El endpoint para el servicio de embeddings en Azure.
   - **AZURE_EMBEDDING_MODEL_ID**: El identificador del modelo de embeddings en Azure.
   - **AZURE_EMBEDDING_API_VERSION**: La versión de la API para embeddings en Azure.

   Ejemplo de cómo se vería el archivo `.env`:

   ```env
   POSTGRES_USER=tu_usuario
   POSTGRES_PASSWORD=tu_contraseña
   AZURE_OPENAI_API_KEY=tu_clave_de_api_azure
   AZURE_DEPLOYMENT_NAME=nombre_del_despliegue
   AZURE_OPENAI_INPUT=entrada_azure
   AZURE_API_VERSION=version_api_azure
   AZURE_OPENAI_MODEL_ID=tu_modelo_id

   AZURE_EMBEDDING_KEY=tu_clave_de_api_embeddings
   AZURE_EMBEDDING_DEPLOYMENT_NAME=nombre_del_despliegue_embeddings
   AZURE_EMBEDDING_ENDPOINT=endpoint_embeddings
   AZURE_EMBEDDING_MODEL_ID=identificador_modelo_embeddings
   AZURE_EMBEDDING_API_VERSION=version_api_embeddings
   ```

## Cómo ejecutar las aplicaciones

Para ejecutar cualquiera de las aplicaciones, sigue estos pasos:

1. Asegúrate de que el entorno Conda correspondiente esté activado.  
2. Desde la carpeta raíz del proyecto, ejecuta el archivo `main.py` de la aplicación deseada.

### Ejemplo para **app_chat**:

1. **Activa el entorno Conda**:

   ```bash
   conda activate appchat_env
   ```

2. **Ejecuta la aplicación**:

   ```bash
   python -m app_chat.main
   ```

---

Este mismo proceso se aplica para las otras dos aplicaciones, solo cambia el nombre de la carpeta y el archivo principal (`app_crawler/main.py` o `app_navigation/main.py`).

1. Activa el entorno Conda correspondiente:
   - Para **AppCrawling**: `conda activate appcrawling_env`
   - Para **AppNavegacion**: `conda activate appnavegacion_env`

2. Ejecuta el archivo `main.py`:
   - Para **AppCrawling**: `python -m app_crawler.main`
   - Para **AppNavegacion**: `python -m app_navigation.main`
   

Así, cada aplicación funcionará de manera independiente, pero el proceso es el mismo.


## Uso

- **AppCrawling** y **AppNavegacion**:  
  Simplemente ejecuta la aplicación y espera a que termine, ya que son aplicaciones de un solo uso.
  Aun asi, puedes modificar la app de navegación con un nuevo instruct.txt y una nueva URL base para testear el proceso en una web de convocatorias distinta.

- **AppChat**:  
  Ejecuta la aplicación y, directamente en la consola donde se haya ejecutado, podrás interactuar con el chat, conversando con el agente.


## Tests

Dependiendo de para que aplicación, seguiremos los siguientes modificando el ejemplo según la aplicación que necesitemos usar.

1. Activa el entorno Conda correspondiente

   - Para **AppCrawling**: `conda activate appcrawling_env`
   - Para **AppNavegacion**: `conda activate appnavegacion_env`
   - Para **AppChat**: `conda activate appchat_env`

2. Seguidamente, desde el directorio base ejecutaremos el siguiente comando para lanzar los tests:

```bash
# Para lanzar los tests de la app de navegación
set PYTHONPATH=. && pytest -s app_navigation/tests/
```

```bash
# Para lanzar los tests de la app de crawler
set PYTHONPATH=. && pytest -s app_crawler/tests/
```

```bash
# Para lanzar los tests de la app de chat
set PYTHONPATH=. && pytest -s app_chat/tests/
```
La -s en estos comandos es importante para ver información mas detallada. Quizas veas que un test ha fallado pero en realidad solo han fallado 5 campos de todo el test, con lo que es un fallo parcial.

Es importante saber, que estos test son pesados de ejecutar, es por ello, que en cada una de las carpetas de tests se guardan capturas de resultados de ejecuciónes de tests.

## Importante

Las aplicaciones **Crawling** y **Navegación** son muy pesadas de ejecutar debido a la gran cantidad de datos que procesan. 

Por ello, se proporcionan **datos precargados** para que puedas utilizar directamente la aplicación **Chat** sin necesidad de ejecutar estas dos aplicaciones pesadas.

Para ello, en el archivo .env, encontraras la variable de entorno USE_BACKUP_DATA. Marca con TRUE si quieres usar datos precargados (por defecto ya esta en TRUE). Ten en cuenta que esta carga elimina los datos ya existentes en ambas bases de datos.

