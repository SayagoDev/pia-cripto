#
# Hecho por Ángel Saúl Sáyago Leiba
#

import click
import os
import time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        run()
    else:
        pass


@cli.command()
@click.option('-k', '--public_key', prompt=True)
@click.option('-p', '--file_path', prompt=True)
@click.option('-c', '--certificado', prompt=True)
def verificar_signature(public_key, file_path, certificado):
    """Función para verificar un certificado '.cer'"""

    try:
        with open(public_key, 'rb') as f:
            public_pem = f.read()

        public_key = serialization.load_pem_public_key(
            public_pem, backend=default_backend()
        )

        with open(file_path, 'rb') as f:
            file_contents = f.read()

        with open(certificado, 'r') as f:
            cert_data = f.read()

        username, signature = cert_data.split("    ")
        signature = bytes.fromhex(signature)

        # Verifica el signature usando la clave publica
        public_key.verify(
            signature,
            file_contents,
            ec.ECDSA(hashes.SHA256())
        )

        os.system("clear || cls")
        click.echo('**********************')
        click.echo('* La firma es válida *')
        click.echo('**********************')
        time.sleep(0.5)

        click.echo('\nUsuario: {}'.format(username))
    except FileNotFoundError:
        click.echo(
            'No se encontró la clave pública para el usuario especificado.')
    except:
        os.system("clear || cls")
        click.echo('*************************')
        click.echo('* La firma no es válida *')
        click.echo('*************************')


def sign_file(username, file_path):
    private_key_file = f"{username}_key.pem"
    password = click.prompt('Contraseña', hide_input=True)
    try:
        with open(private_key_file, 'rb') as f:
            private_pem = f.read()

        private_key = serialization.load_pem_private_key(
            private_pem,
            password=password.encode(),
            backend=default_backend()
        )

        with open(file_path, 'rb') as f:
            file_contents = f.read()

        signature = private_key.sign(
            file_contents,
            ec.ECDSA(hashes.SHA256())
        )

        # Agregamos el usuario al signature. Al momento
        # de certificar el archivo, nos indique quien los firmo
        cert_data = f"{username}    {signature.hex()}"

        # Guarda el signature en un archivo con extensión .cer
        temp_name = file_path.replace(".txt", "")
        signature_file = f"{temp_name}.cer"
        with open(signature_file, 'w') as f:
            f.write(cert_data)

        os.system("clear || cls")
        click.echo('\n********************************')
        click.echo('* Archivo firmado exitosamente *')
        click.echo('********************************')
        time.sleep(0.5)

        click.echo('.')
        click.echo(
            '\nLa firma se ha guardado en el archivo: {}'.format(signature_file))
    except FileNotFoundError:
        click.echo(
            'No se encontró la clave privada para el usuario especificado.')


@cli.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def register(password, username):
    """Función para crear nuevas claves criptográficas"""

    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    public_key = private_key.public_key()

    private_key_file = f"{username}_key.pem"
    public_key_file = f"{username}_pub.pem"

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode())
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(private_key_file, 'wb') as f:
        f.write(private_pem)

    with open(public_key_file, 'wb') as f:
        f.write(public_pem)

    os.system("clear || cls")
    click.echo('\n*********************')
    click.echo('* Registro completado *')
    click.echo('*********************')
    click.echo('\nClave privada cifrada guardada en el archivo: {}'.format(
        private_key_file))
    click.echo('Clave pública guardada en el archivo: {}'.format(public_key_file))


@cli.command()
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def login(username, password):
    """Función para iniciar sesión con usuario, contraseña y sus certificados"""
    private_key_file = f"{username}_key.pem"
    public_key_file = f"{username}_pub.pem"

    try:
        with open(private_key_file, 'rb') as f:
            private_pem = f.read()

        with open(public_key_file, 'rb') as f:
            public_pem = f.read()

        private_key = serialization.load_pem_private_key(
            private_pem,
            password=password.encode(),
            backend=default_backend()
        )
        public_key = serialization.load_pem_public_key(
            public_pem, backend=default_backend())

        os.system("clear || cls")
        click.echo('\n****************************')
        click.echo('* Inicio de sesión exitoso *')
        click.echo('****************************')
        time.sleep(1)
        os.system("clear || cls")

        while True:
            click.echo('--- Menú ---')
            click.echo('1. Firmar archivo')
            click.echo('2. Salir')

            choice = click.prompt('Elige una opción', type=int)
            if choice == 1:
                file_path = click.prompt('\nRuta del archivo a firmar')
                sign_file(username, file_path)
            elif choice == 2:
                break
            else:
                click.echo('Opción inválida. Inténtalo de nuevo.')

        os.system("clear || cls")
        click.echo('\n*********************')
        click.echo('* Sesión finalizada *')
        click.echo('*********************')
    except FileNotFoundError:
        click.echo('\nNo se encontraron claves para el usuario especificado.')
    except ValueError:
        click.echo('\nContraseña incorrecta.')


def run():
    while True:
        os.system("clear || cls")
        click.echo('--- Menú ---')
        click.echo('1. Iniciar Sesión')
        click.echo('2. Registrarse')
        click.echo('3. Validar un certificado')
        click.echo('4. Salir')

        choice = click.prompt('Elige una opción', type=int)

        if choice == 1:
            os.system("clear || cls")
            login()
        elif choice == 2:
            os.system("clear || cls")
            register()
        elif choice == 3:
            os.system("clear || cls")
            verificar_signature()
        elif choice == 4:
            os.system("clear || cls")
            break
        else:
            click.echo('Opción inválida. Inténtalo de nuevo.')


if __name__ == '__main__':
    cli()
