import os
import shutil
import sqlite3
from datetime import datetime

import click

from config import BASE_DIR

DEFAULT_BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DB_PATH = os.path.join(BASE_DIR, 'data', 'holocron.db')
UPLOADS_DIR = os.path.join(BASE_DIR, 'app', 'static', 'uploads')


def make_backup(dest_root=DEFAULT_BACKUP_DIR):
    """Copy the database and uploaded covers into a new dated folder; return its path."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f'Database not found: {DB_PATH}')

    folder = os.path.join(dest_root, datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    os.makedirs(folder)

    # sqlite3's backup API gives a consistent copy even if the app is running
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(os.path.join(folder, 'holocron.db'))
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    if os.path.isdir(UPLOADS_DIR):
        shutil.copytree(UPLOADS_DIR, os.path.join(folder, 'uploads'))
    return folder


def register_backup_command(flask_app):
    @flask_app.cli.command('backup')
    @click.option('--dest', default=DEFAULT_BACKUP_DIR, show_default=True,
                  help='Folder that receives the dated backup folders.')
    def backup_command(dest):
        """Save a dated copy of the database and cover images."""
        folder = make_backup(dest)
        click.echo(f'Backup saved to {folder}')
