import shutil
import tempfile

from os import mkdir, listdir
from os.path import join, abspath
from datetime import datetime

import numpy as np

from typing import Tuple

from mtpy.modeling import occam1d, occam2d

from utils.occam_plotting import create_iter_files

from bin.occam import (
    last_iter_filename,
    run_occam1d,
    run_occam2d,
)


def create_startup_file_occam2d(
        edi_path: str,
        save_path: str,
        station_list,
        **kwargs,
) -> None:
    pass


def create_startup_draft(edi_path: str, save_path: str) -> None:
    station_list = [edi[0:-4] for edi in listdir(edi_path) if edi.find('.edi') > 0]

    print(station_list)

    occam_data = occam2d.Data(edi_path=edi_path,
                              station_list=station_list,
                              interpolate_freq=True,
                              freq=np.logspace(-3, 3, 37))

    occam_data.save_path = save_path
    occam_data.geoelectric_strike = 0.1

    occam_data.res_te_err = 10
    occam_data.phase_te_err = 5

    occam_data.res_tm_err = 10
    occam_data.phase_te_err = 5

    occam_data.model_mode = '1'

    occam_data.write_data_file()

    occam_reg = occam2d.Regularization(occam_data.station_locations)

    occam_reg.n_layers = 60
    occam_reg.cell_width = 1250

    occam_reg.x_pad_multiplier = 1.2
    occam_reg.trigger = 0.25
    occam_reg.z_bottom = 200000
    occam_reg.z1_layer = 50
    occam_reg.z_target_depth = 80000
    occam_reg.save_path = occam_data.save_path

    occam_reg.build_mesh()
    occam_reg.build_regularization()
    occam_reg.write_mesh_file()
    occam_reg.write_regularization_file()

    occam_startup = occam2d.Startup()
    occam_startup.iterations_to_run = 100
    occam_startup.resistivity_start = 2.0
    occam_startup.target_misfit = 1.2
    occam_startup.data_fn = join(occam_data.data_fn)
    occam_reg.get_num_free_params()
    occam_startup.param_count = occam_reg.num_free_param
    occam_startup.save_path = occam_data.save_path
    occam_startup.model_fn = occam_reg.reg_fn
    occam_startup.write_startup_file()


if None:
    edi_path = '../informe/mtpy_proj/mtpy-edis/'
    save_path = '../informe/mtpy_proj/plots/occam2d_2/'

    create_startup_draft(edi_path=abspath(edi_path),
                         save_path=abspath(save_path))

    create_iter_files(save_file_path=save_path,
                      startup_file_path=save_path,
                      model='occam2d',
                      occam_bin_path='../bin/occam/')

if None:
    plot_model = occam2d.PlotModel(iter_fn='../informe/mtpy_proj/plots/occam2d_2/iterfiles_occam2d/ITER04.iter',
                                   data_fn='../informe/mtpy_proj/plots/occam2d_2/OccamDataFile.dat',
                                   station_font_pad=2.5,
                                   station_font_size=4,
                                   station_font_rotation=90,
                                   font_size=4,
                                   climits=(0, 4),
                                   xpad=0.25,
                                   yscale='m',
                                   yminorticks=0.250,
                                   dpi=300,
                                   fig_aspect=0.25,
                                   ylimits=(-2, 20),
                                   station_id=(-1, 5))
    plot_model.save_figure('../informe/mtpy_proj/plots/occam2d_plotmodel_2.png')


if __name__ == '__main__':
    plot_model = occam2d.PlotModel(iter_fn='../../plots/occam2dtest/iterfiles_occam2d/ITER25.iter',
                                   data_fn='../../plots/occam2dtest/OccamDataFile.dat',
                                   station_font_pad=2.5,
                                   station_font_size=4,
                                   station_font_rotation=90,
                                   font_size=4,
                                   climits=(0, 4),
                                   xpad=0.25,
                                   yscale='m',
                                   yminorticks=0.250,
                                   dpi=300,
                                   fig_aspect=0.25,
                                   ylimits=(-2, 20),
                                   station_id=(-1, 5))

    plot_model.save_figure('../informe/mtpy_proj/plots/occam2d_plotmodel_2.png')
