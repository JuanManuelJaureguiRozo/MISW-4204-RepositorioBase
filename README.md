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

1. Para realizar el despliegue en la nube haciendo uso de balanceador de cargas y autoscalling realizamos el proceso inicial de configurar una VM con el servicio de modo tal que pudieramos hacer uso de su dico como imagen para que un grupo de instancias pudiera escalar de accuerdo a los criterios definidos, ahora bien, antes de intentar ejecutar los microservicios es recomendable instalar las diferentes librerías utilizadas en la aplicación, para ellos ubiquese en la raíz del repositorio MISW-4204-RepositorioBas donde encontrará el archivo "requirements.txt" y ejecute la instrucción:
```bash
sudo python3 -m pip install -r requirements.txt
```

2. Para el caso de sudo pip install psycopg2 se debe realizar su instalación de manera independiente ya que generaba error dentro de los requeriments.
```bash
sudo pip install psycopg2-binary
```

3. En caso de presentar error con alguna librería en particular recuerde ejecutar su instalación
```bash
sudo pip install opencv-python
sudo pip install redis
```

4. Recuerde realizar la configuración correspondiente en los archivo config.ini de cada microservicio con el objetivo de configurar credenciales de conexión a la instancia de base de datos, informacción del bucket y path definidos para guardar los vídeos.

5. Instale gunicorn para exponer el servicio web-server externamente
```bash
sudo pip install gunicorn
```

6. Hicimos uso del puerto 5000 en caso de requerir habilitar o permitir trafico por un puerto en particular instale ufw y haga uso del comando
```bash
sudo apt install ufw
sudo ufw allow 5000
```

7. Para crear la aplicación como servicio con el objetivo de mantenerlo en ejecución instale la utilidad pm2
```bash
sudo npm install pm2@latest -g
```

8. De ser necesario modifique el archivo microservicio_recibir_video/datos/api_commands.py con la IP del servidor de Redis para la creación de las tareas a procesar por los microservicio cargarVideo y editarVideo.

9. Para establecer la aplicación web-server (microservicio recibirVideo) ubiquese en la carpeta microservicio_recibir_video y ejecute el comando
```bash
pm2 start "sudo gunicorn --bind 0.0.0.0:5000 app:app" --name web-server
```

10. En este punto tomamos la instancia acondicionada actual para hacer uso de su disco en la creación de la imagen que permitirá crear la plantilla para el grupo de servicios que escalará esta capa de la aplicación

11. Ahora, para los microservicios que ejecutan procesos en batch luego de seguir los pasos anteriores del 1 al 4 incluyendo el paso 7, podemos registrar como servicios los worker para cargar y editar los vídeos de la siguiente manera.

En la ubicación MISW-4204-RepositorioBase/microservicio_cargar_video
```bash
pm2 start "sudo celery -A app.celery_app  worker -l info -P solo -Q upload -n worker_upload" --name upload_video
```

En la ubicación MISW-4204-RepositorioBase/microservicio_editar_video
```bash
pm2 start "sudo celery -A app.celery_app  worker -l info -P solo -Q edit -n worker_edit" --name edit_video
```

# **Despliegue en la nube haciendo del servicio de mensajería PUBSUB**

Para realizar el despliegue en la nube haciendo uso del servicio de mensajeria, se aplicó el mismo despliegue de la entrega anterior con alguna pequeñas diferencias que serán mencionadas a continuación:
1. Instalaciónd e librerías de GCP para el uso de este servicio
```bash
sudo pip install google-cloud
sudo pip install google-cloud-pubsub
```   
2. Luego de las modificaciones realizadas en el código fuente del proyecto, la única diferencia para subir el servicio se dió en el microservicio editarVideo, para el cual fue necesario especificar un timeout en su publicación en gunicorn paara evitar errores en el procesamiento de mensajes de edición de vídeos, adicional a que anteriormente la instrucción correspondía a el levantamiento de la cola y en este caso a la ejecución de la aplicación Flask
```bash
sudo pm2 start "sudo gunicorn --bind 127.0.0.1:5002 app:app --workers 1 --timeout 180" --name edit-server
```  
3. Persistir los servicios en sudo para que luego de detener las VM estos se levantaran de manera automatica una vez se iniciaran nuevamente.
```bash
sudo pm2 startup systemd
sudo pm2 save
sudo systemctl start pm2-root
sudo systemctl stop pm2-root
sudo systemctl status pm2-root
```  

# **Despliegue en la nube haciendo uso de plataforma como servicio CLOUD RUN**

Para el despliegue se realizó la modificación del código fuente de cada microservicio con el objetivo de asegurar su funcionamiento en cloud run, para el caso solo es requerido por cada microservicio ejecutar la instrucción:
```bash
gcloud run deploy
```
Es necesario tener en cuenta que nos debemos ubicar en la carpeta raíz de cada microservicio para poder ejecutar dicha instrucción, por defecto usamos los siguientes nombres:
1. webserver
2. uploadvideo
3. editvideo

Todos fueron desplegados en la región 37 correspondiente a us-west1 con la configuración *Permitir sin autenticación*   
