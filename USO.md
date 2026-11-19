# Inventario Tecnológico — Centinela SOC

Proyecto final de Servidores II. Centinela SOC es una empresa **ficticia** de ciberseguridad. El inventario inicial contiene 12 equipos de ejemplo.

## Iniciar desde cero

Se necesita Docker con Docker Compose y el puerto 80 disponible. El archivo `.env` local contiene credenciales solo para desarrollo y está ignorado por Git. En otra instalación, copia `.env.example` a `.env` y cambia ambas contraseñas.

```sh
docker compose down -v
docker compose up -d --build
```

Abre http://localhost. La ruta http://localhost/salud responde `OK` con código 200 cuando la app y MySQL están disponibles.

`down -v` borra el volumen `db_data` y vuelve a cargar los 12 equipos desde `init.sql`. Para conservar datos, usa `docker compose down` sin `-v`.

La página de inicio muestra totales por tipo y estado. En **Equipos** puedes filtrar, buscar, cambiar estado, editar y eliminar con confirmación. **Agregar equipo** abre el formulario de alta.

Nginx es el único servicio que publica un puerto. Flask corre con Gunicorn como usuario sin privilegios y MySQL guarda los datos en `db_data`. Los tres servicios comparten una red bridge interna.

## Publicar una versión

Crea los secretos `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` en GitHub. El token debe poder publicar en el repositorio `inventario-centinela` de ese usuario. Después, publica un tag:

```sh
git tag v1.0 && git push origin v1.0
```

El workflow publica las etiquetas `1.0` y `latest`. También puede ejecutarse manualmente indicando la versión sin `v`. En el servidor, configura `DOCKERHUB_USER` y `APP_VERSION` en `.env` y actualiza con:

```sh
docker compose pull app && docker compose up -d
```
