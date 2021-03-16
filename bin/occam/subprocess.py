from os import listdir
from os.path import join, abspath
from shutil import copy

import re
import subprocess

from typing import Tuple

occam_files = {
    'OCCAM1DCSEM',
    'Occam2D',
    'DIPOLE1D',
}

startup_files_occam1d = {
    'Occam1d_DataFile_DET.dat',
    'Model1D',
    'OccamStartup1D',
}

startup_files_occam2d = {
    'Occam2DMesh',
    'Occam2DModel',
    'Occam2DStartup',
    'OccamDataFile.dat',
}


def run_occam1d(
        occam_path: str,
        startup_path: str,
        tempdir: str,
) -> None:
    """
    Copia los binarios occam y archivos de startup en un directorio 'tempdir' y
    abre un subproceso './OCCAM1DCSEM' en ese mismo directorio.
    """

    for file in occam_files:
        try:
            copy(join(occam_path, file), tempdir)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'No se encontró el archivo {file}. Error en la instalación.')

    for file in startup_files_occam1d:
        copy(join(startup_path, file), tempdir)

    occam = subprocess.run(["./OCCAM1DCSEM", "OccamStartup1D"],
                           cwd=tempdir)


def run_occam2d(
        occam_path: str,
        startup_path: str,
        tempdir: str,
) -> None:
    """
    Copia los binarios occam y archivos de startup en un directorio 'tempdir' y
    abre un subproceso './Occam2D' en ese mismo directorio.
    """

    for file in occam_files:
        try:
            copy(join(occam_path, file), tempdir)
        except FileNotFoundError as e:
            raise FileNotFoundError(f'No se encontró el archivo {file}. Error en la instalación.') from e

    for file in startup_files_occam2d:
        copy(join(startup_path, file), tempdir)

    occam = subprocess.run(["./Occam2D", "Occam2DStartup"],
                           cwd=tempdir)


def last_iter_filename(tempdir: str) -> Tuple[str, str]:
    """
    Extrae el número de la última iteración y devuelve una tupla
    con el nombre de los archivos.
    """

    """ 
    Expresión regular para buscar el patrón 'ITER_' + (número) + '.resp/iter'.
    No incluye ni a 'ITER_' ni a la extensión en la búsqueda.
    """

    pattern = re.compile(r'(?<=(ITER)_)[\d]+(?=.(resp|iter))')

    numbers = []

    for file_name in listdir(tempdir):
        search = pattern.search(file_name)

        if search is not None:
            numbers.append(int(search.group()))

    return f'ITER_{max(numbers)}.iter', f'ITER_{max(numbers)}.resp'

