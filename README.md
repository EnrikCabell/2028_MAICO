# MAICO

Aplicación para gestionar clientes, estudios audiológicos, citas y búsquedas de expedientes.

## Modo de prueba

Si no existe la variable `DATABASE_URL`, la aplicación inicia en modo de prueba y guarda registros en `maico_demo.db`. En Streamlit Cloud ese archivo no debe considerarse almacenamiento permanente.

## Base permanente

Cuando se configure PostgreSQL, agrega en Streamlit → Settings → Secrets:

```toml
DATABASE_URL = "postgresql://usuario:contraseña@servidor:5432/base?sslmode=require"
```

La aplicación detecta la conexión y utiliza PostgreSQL automáticamente.

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```
