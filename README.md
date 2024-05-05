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
3. Ubicarse en el microservicio microservicio_cargar_video y subir Celery que ejecutará la cola "upload" que corresponde al proceso en batch para la carga del vídeo en repositorio
```bash
celery -A app.celery_app  worker -l info -P solo -Q upload
```
4. Ubicarse en el microservicio microservicio_editar_video y subir Celery que ejecutará la cola "edit" que corresponde al proceso en batch para la edicción del vídeo
```bash
celery -A app.celery_app  worker -l info -P solo -Q edit
```
5. En el archivo config.ini de cada microservicio encontrará el parametro "file_upload_dir" donde podrá configurar la ruta de guardado del los vídeos originales y editados

Finalmente, a continuación se comparte enlace a la colección de request para usar desde postman y el script de creación de la tabla en la base de datos IDRL
https://uniandes.sharepoint.com/:f:/s/Desarrollodesoftwareenlanube397/Eh6Do18KnSROteatsJxahYsBM8ZLgB_belb-mTnm3mukEw?e=1mDlOs

# **Despliegue en la nube haciendo de Buckets**

Para realizar el despliegue en la nube haciendo uso de balanceador de cargas y autoscalling realizamos el proceso inicial de configurar una VM con el servicio de modo tal que pudieramos hacer uso de su dico como imagen para que un grupo de instancias pudiera escalar de accuerdo a los criterios definidos, ahora bien, antes de intentar ejecutar los microservicios es recomendable instalar las diferentes librerías utilizadas en la aplicación, para ellos ubiquese en la raíz del repositorio MISW-4204-RepositorioBas donde encontrará el archivo "requirements.txt" y ejecute la instrucción:
```bash
sudo python3 -m pip install -r requirements.txt
```

Para el caso de sudo pip install psycopg2 se debe realizar su instalación de manera independiente ya que generaba error dentro de los requeriments.
```bash
sudo pip install psycopg2-binary
```

En caso de presentar error con alguna librería en particular recuerde ejecutar su instalación
```bash
sudo pip install opencv-python
sudo pip install redis
```

Recuerde realizar la configuración correspondiente en los archivo config.ini de cada microservicio con el objetivo de configurar credenciales de conexión a la instancia de base de datos, informacción del bucket y path definidos para guardar los vídeos.

Instale gunicorn para exponer el servicio web-server externamente
```bash
sudo pip install gunicorn
```

Hicimos uso del puerto 5000 en caso de requerir habilitar o permitir trafico por un puerto en particular instale ufw y haga uso del comando
```bash
sudo apt install ufw
sudo ufw allow 5000
```

Para crear la aplicación como servicio con el objetivo de mantenerlo en ejecución instale la utilidad pm2
```bash
sudo npm install pm2@latest -g
```

En este punto para establecer la aplicación web-server (microservicio recibirVideo) ubiquese en la carpeta microservicio_recibir_video y ejecute el comando
```bash
pm2 start "sudo gunicorn --bind 0.0.0.0:5000 app:app" --name web-server
```

En este punto tomamos la instancia acondicionada actual para hacer uso de su disco en la creación de la imagen que permitirá crear la plantilla para el grupo de servicios que escalará esta capa de la aplicación

Ahora, para los microservicios que ejecutan procesos en batch luego de seguir

pm2 start "sudo celery -A app.celery_app  worker -l info -P solo -Q upload -n worker_upload" --name upload_video
pm2 start "sudo celery -A app.celery_app  worker -l info -P solo -Q edit -n worker_edit" --name edit_video
