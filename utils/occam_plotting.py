import shutil
import tempfile

from os import mkdir
from os.path import join, isfile, split, exists
from datetime import datetime

from typing import Tuple

from mtpy.modeling import occam1d

from bin.occam import (
    last_iter_filename,
    run_occam1d,
    run_occam2d,
)

import numpy as np


def create_startup_file_occam1d(
        edi_file: str,
        save_path: str,
        write_data_options: dict,
        startup_options: dict,
        model_options: dict,
) -> None:
    # TODO: Documentación de la función
    occam_data = occam1d.Data()
    occam_data.write_data_file(edi_file=edi_file,
                               save_path=save_path,
                               **write_data_options)

    occam_model = occam1d.Model(**model_options)

    occam_model.write_model_file(save_path=save_path)

    occam_startup = occam1d.Startup(data_fn=occam_data.data_fn,
                                    model_fn=occam_model.model_fn,
                                    **startup_options)

    occam_startup.write_startup_file()


def plot_occam1d(
        edi_file: str,
        save_path: str,
        plot_format: dict,
        #iter_n: int,
        **kwargs
):
    # TODO: Documentación de la función
    time = ( datetime.now() ).strftime("%Y-%m-%d %H:%M")

    # mover esto
    new_dir = join(save_path, time + '_OCCAM1DPLOT')

    mkdir(new_dir)

    create_startup_file_occam1d(edi_file, new_dir, **kwargs)
    # mover esto^^

    dot_iter, dot_resp = create_iter_files(save_file_path=new_dir,
                                           startup_file_path=new_dir,
                                           model='occam1d',
                                           occam_bin_path='../bin/occam/')

    model_fn = join(new_dir, 'Model1D')
    data_fn = join(new_dir, 'Occam1d_DataFile_DET.dat')

    occam_model = occam1d.Model(model_fn=model_fn)
    occam_model.read_iter_file(dot_iter)

    occam_data = occam1d.Data(data_fn=data_fn)
    occam_data.read_data_file(data_fn=data_fn)
    occam_data.read_resp_file(resp_fn=dot_resp)

    plot = occam1d.Plot1DResponse(data_te_fn=data_fn,
                                  data_tm_fn=data_fn,
                                  model_fn=model_fn,
                                  resp_te_fn=dot_resp,
                                  iter_te_fn=dot_iter,
                                  depth_limits=(0, 1)) # TODO: extraer esto

    # TODO: revisar esto
    plot.save_figure(new_dir, **plot_format)


def plot_l2_curve(model_fn: str, iter_path: str, save_dir: str):
    #TODO: Documentar función
    plot = occam1d.PlotL2(model_fn=model_fn,
                          dir_path=iter_path)

    plot.save_figure(file_format='png',
                     fig_dpi=400,
                     save_fn=save_dir)


def create_iter_files(
        startup_file_path: str,
        save_file_path: str,
        model: str,
        occam_bin_path: str,
        tempdir: str = None,
) -> Tuple[str, str]:
    # TODO: Documentar función
    #with tempfile.TemporaryDirectory() as tempdir:
    if model not in {'occam1d', 'occam2d'}:
        raise ValueError("El argumento 'model' debe ser un string 'occam1d' u 'occam2d'")

    if tempdir is None:
        new_dir = join(save_file_path, 'iterfiles_' + model)

        mkdir(new_dir)
        working_dir = new_dir
    else:
        working_dir = tempdir

    """ 
    TODO: Refactorizar occam1d/occam2d y hacer que la función se encargue de asignar el modelo
    a ejecutar.
    """
    # Por claridad, lo hago explícito
    if model == 'occam1d':
        run_occam1d(occam_bin_path,
                    startup_file_path,
                    working_dir)
    elif model == 'occam2d':
        run_occam2d(occam_bin_path,
                    startup_file_path,
                    working_dir)

    dot_iter, dot_resp = last_iter_filename(working_dir)

    if tempdir is not None:
        shutil.copy(dot_iter, save_file_path)
        shutil.copy(dot_resp, save_file_path)

        dot_iter = join(save_file_path, dot_iter)
        dot_resp = join(save_file_path, dot_resp)
    else:
        # TODO: Limpiar los archivos copiados en working_dir
        dot_iter = join(working_dir, dot_iter)
        dot_resp = join(working_dir, dot_resp)

    return dot_iter, dot_resp



if None:
    write_data_options = {
        'mode': 'det',
        'res_errorfloor': 10,
        'phase_errorfloor': 5,
        'remove_outofquadrant': True
    }

    model_options = {
        'n_layers': 18,
        'target_depth': 500,
        'bottom_layer': 1000,
        'z1_layer': 10,
        'freq': np.logspace(2.4, 30),
    }

    startup_options = {
        'max_iter': 200,
        'target_rms': 1.0,
    }

    plot_format = {
        'file_format': 'png',
        'fig_dpi': 1600,
    }

    occam_1d_options = {
        'model_options': model_options,
        'write_data_options': write_data_options,
        'startup_options': startup_options,
        'plot_format': plot_format,
    }

    plot_occam1d(edi_file="../informe/mtpy_proj/mtpy-edis/MC1_1.edi",
                 save_path="../informe/mtpy_proj/plots/",
                 #iter_n=1,
                 **occam_1d_options)


def serialize_occam1d_model(
        model_path: str,
        iter_path: str,
        save_path: str = None,
) -> None:
    if save_path is None:
        save_path = './'

    if isfile(save_path):
        save_path, filename = split(save_path)
    else:
        # Nombre del archivo por defecto
        filename = 'resdepth.txt'

    if exists(join(save_path, filename)):
        raise FileExistsError('Ya existe un archivo con el mismo nombre.')

    model = occam1d.Model()
    model.read_model_file(model_path)
    model.read_iter_file(iter_path)

    with open(join(save_path, filename), 'w') as file:
        index = 0

        # El atributo model_res tiene una columna entera de 'freeparams'
        for (freeparams, resistivity), depth in zip(model.model_res, model.model_depth):
            if index: # La primera file no se consideraba en el método original
                file.write(f'{10 * resistivity:.5f} {depth}\n')

            index += 1


if __name__ == '__main__':
    plot_l2_curve(model_fn='/home/duskje/PycharmProjects/georesource/georesource/informe/mtpy_proj/plots/2021-03-12 06:07_OCCAM1DPLOT/Model1D',
                  iter_path='/home/duskje/PycharmProjects/georesource/georesource/informe/mtpy_proj/plots/2021-03-12 06:07_OCCAM1DPLOT/iterfiles_occam1d',
                  save_dir='/home/duskje/PycharmProjects/georesource/georesource/informe/mtpy_proj/plots/L2_plot.png')
