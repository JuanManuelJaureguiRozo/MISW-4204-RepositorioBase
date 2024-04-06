# Users

Este microservicio se encarga de manejar todo lo relacionado a los usuarios del proyecto. Se pueden crear usuarios, generar tokens, actualizar usuarios, obtener el estado del microservicio y reiniciar su base de datos. Este microservicio fue desarrollado utilizando Flask e integra Postgres como su base de datos.

## Índice

1. [Estructura](#estructura)
2. [Ejecución](#ejecución)
3. [Uso](#uso)
4. [Pruebas](#pruebas)
5. [Autor](#autor)

## Estructura

Esta es la estructura de carpetas que tiene nuestro proyecto:



.
├── src
│   ├── blueprints
│   │   └── Users
│   │       ├── [Archivos de pruebas de los blueprints del microservicio  Users]
│   ├── commands
│   │   └──  Users
│   │       ├── [Archivos de pruebas de los comandos del microservicio  Users]
│   ├──errors
│   │   └──  Users
│   │       ├── [Archivos de pruebas de las utilidades del microservicio  Users]
│   ├──models
│   │   └──  Users
│   │       ├── [Archivos de pruebas de las utilidades del microservicio  Users]

├──__init__.py

├──main.py

├──session.py
├── tests
│   ├── blueprints
│   │   └── Users
│   │       ├── [Archivos de pruebas de los blueprints del microservicio  Users]
│   ├── commands
│   │   └──  Users
│   │       ├── [Archivos de pruebas de los comandos del microservicio  Users]
│   ├── utils
│   │   └──  Users
│   │       ├── [Archivos de pruebas de las utilidades del microservicio  Users]
│   ├── __init__.py
│   ├── conftest.py
│   └── mocks.py
├── __init__.py
├── .dockerignore
├── .env.template
├── .env.test
├── Dockerfile
├── Pipfile
└── README.md

## Ejecución

Para ejecutar el microservicio, se debe primero construir la imagen asociada a este y posteriormente se debe ejecutar el archivo docker-compose.yaml ubicado en la raíz del proyecto.

## Uso

Para poder utilizar el microservicio, lo primero que se debe hacer es crear la imagen de la base de datos y de offers. Para eso, debemos ubicarnos en la raíz del proyecto y en una terminal ejecutar los siguientes comandos:

docker pull postgres
docker build -t offers

De esta manera, se tendrán todas las imágenes necesarias para poder usar el microservicio. Ahora bien, para deesplegarlo, se utiliza el siguiente comando:

docker-compose up

Listo! El microservicio debería estar funcionando bien en tu máquina. Sin embargo, ten en cuenta que algunas funcionalidades dependen de los otros microservicios, por lo cual, puedes llegar a obtener errores. Puedes revisar esto en la aplicación de Docker verificando que los contenedores y la imagen se crearon correctamente.

## Autor

Óscar Álvarez
