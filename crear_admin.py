import os
import django

# Configuramos el entorno de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Datos del superusuario (Cámbialos aquí si quieres)
USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@kine.com')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

def crear_superusuario():
    if not User.objects.filter(username=USERNAME).exists():
        print(f"Creando superusuario: {USERNAME}...")
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print("¡Superusuario creado con éxito!")
    else:
        print("El superusuario ya existe. No se hace nada.")

if __name__ == "__main__":
    crear_superusuario()