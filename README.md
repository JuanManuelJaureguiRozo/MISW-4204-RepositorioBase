# **Integrantes**

* Ever Martínez
* Eduar Romero
* Juan Manuel Bermudez
* Juan Manuel Jáuregui

Para la ejecución del servicio y la cola de mensajería ejecute los siguiente pasos:

Previo a la ejecución de los pasos asegurese de tener postgressql instalado y haber creado el usuario "postgres" con la contraseña "postgresql"

0. Creación y activación  del entorno de trabajo en Python en Windows
```bash
py -m venv venv 
venv/Scripts/activate
```
1. Instalación de dependencias del proyecto
```bash
py -m pip install -r requirements.txt
```
1.1. En caso de algún error en la instalación de alguna dependencia se recomienda realizar su instalación de manera independiente, ejemplo.
```bash
py -m pip install psycopg2
```
2. Ubicarse en el microservicio microservicio_recibir_video y ejecutarlo
```bash
flask run -p 5001
```
3. Ubicarse en el microservicio microservicio_cargar_video y subir Celery que ejecutará los procesos en batch
```bash
celery -A app.celery_app  worker -l info -P solo -Q logs
```

Finalmente, a continuación se comparte enlace a la colección de request para usar desde postman y el script de creación de la tabla en la base de datos IDRL
https://uniandes.sharepoint.com/:f:/s/Desarrollodesoftwareenlanube397/Eh6Do18KnSROteatsJxahYsBM8ZLgB_belb-mTnm3mukEw?e=1mDlOs