# EXPLICACIÓN DE FUNCIONAMIENTO


La aplicación implementa un sistema CRUD (*Create, Read, Update, Delete*) utilizando servicios *serverless* de Amazon Web Service  (en adelante AWS). El objetivo es permitir la gestión de los registros mediante una interfaz web.

La solución aprovecha los servicios gestionados por AWS que escalan automáticamente según la demanda y reducen tareas de administración y mantenimiento.

## Arquitectura 

La solución esta compuesta por los siguientes servicios:

- **Amazon S3**: Alojamiento del front-end estático (compuesto por HTML, CSS y JS)
- **Amazon API Gateway**: publicación de la API REST usada por el Frontend.
- **AWS Lambda**:  Ejecución lógica de negocio y procesamiento de solicitudes
- **Amazon DynamoDB**: Almacenamiento persistente de los datos.


La arquitectura sigue el siguiente flujo

```mermaid
flowchart TD
    U[Usuario]
    S3[Amazon S3<br>Frontend HTML/CSS/JS]
    APIGW[Amazon API Gateway]
    L[AWS Lambda<br>CRUD]
    DDB[Amazon DynamoDB<br>ItemsSam]

    U -->|HTTPS| S3
    S3 -->|REST API| APIGW
    APIGW -->|Lambda Proxy| L
    L -->|boto3| DDB
    DDB --> L
    L --> APIGW
    APIGW --> S3
```

## Explicación del flujo

1. El usuario accede a la aplicación web alojada en el S3 a través del navegador.
2. El *frontend* muestra la interfaz y le permite hacer las diferentes operaciones CRUD sobre los datos.
3. Cuando el usuario realiza una de las acciones, el navegador envía una petición HTTP hacia la API Gateway
4. API Gateway  actúa como punto único de entrada y recibe todas las solicitudes externas mediante HTTPS
5. API Gateway redirige la petición a la función Lambda correspondiente usando la integración Lambda Proxy.
6. La función Lambda procesa la solicitud , valida los datos y ejecuta la operación necesaria por DynamoDB.
7. DynamoDB almacena o recupera la información solicitada
8. Lambda genera una respuesta en formato JSON y la devuelve a API Gateway.
9. API Gateway envia la respuesta al navegador del usuario.
10. El *frontend* actualiza la interfaz.

## Papel del API Gateway

En esta arquitectura no se utiliza un balanceador de carga tradicional porque no existen instancias EC2 ni contenedores detras de la aplicación.

API Gateway cumple la función de proxy inverso gestionado por AWS y proporciona:

- Recepción de solicitudes HTTP y HTTPS.
- Gestión de rutas y métodos HTTP.
- Integración con funciones Lambda.
- Configuración de CORS.
- Gestión centralizada del acceso de la API
- Escalado automático.

Además, Lambda escala automaticamente según el número de solicitudes recibidas, por lo que no es necesario implementar mecanismos adicionales de balanceo de carga.

## Seguridad de la arquitectura

Esta arquitectura trata de minimizar la superficie de exposición a Internet.

- El único elemento accesible es el API Gateway mediante https
- No se puede acceder directamente a la función lambda a través de internet
- DynamoDB no expone puertos ni conexiones públicas
- No se requiere acceso por SSH ni apertura de puertos.
- La comunicación entre los servicios de AWS se realiza mediante permisos IAM y servicios gestionados.

## Despliegue manual

El despliegue se realiza siguiendo los siguientes pasos:

### 1. Creación de la tabla DynamoDB

Se crea una tabla en Amazon DynamoDB que almacenará los registros gestionados por la aplicación.

Durante esta configuración se define: 

- Nombre de la tabla
- Clave Primaria
- Configuración de capacidad bajo demanda

### 2. Creación de la función lambda

Se crea una función Lambda usando Python como lenguaje de programación.

La función contiene:

* La lógica CRUD.
* La conexión con DynamoDB mediante boto3.
* El procesamiento de eventos enviados por API Gateway.
* La generación de respuestas JSON para el frontend.

### 3. Configurar la API Gateway

Se crea una API REST y se configuran las rutas necesarias.

Cada ruta se asocia a la función Lambda correspondiente mediante integración Lambda Proxy.

También se configuran:

* Métodos HTTP.
* Parámetros de ruta.
* Respuestas HTTP.
* Configuración CORS.


### 4. Subir el *frontend* a Amazon S3

Se crea un bucket S3 configurado como Static Website Hosting.

Posteriormente se cargan los archivos del frontend:

* index.html
* styles.css
* script.js
* docs.html

El bucket proporciona una URL pública desde la que los usuarios pueden acceder a la aplicación.

### 5. Configurar CORS

Se habilita CORS para permitir que el frontend alojado en S3 pueda consumir la API publicada en API Gateway.

Esta configuración permite que el navegador autorice las solicitudes entre ambos servicios, evitando errores de seguridad relacionados con el mismo origen (Same-Origin Policy).

## Despliegue automático
