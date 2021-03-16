from mtpy.core.mt import MT
from mtpy.analysis.geometry import dimensionality, strike_angle
from mtpy.imaging.plotstrike import PlotStrike
from mtpy.imaging import penetration_depth1d, penetration_depth2d, penetration_depth3d
from mtpy.core.edi_collection import EdiCollection

from typing import Generator
import os

from os.path import (
    abspath, splitext, join, basename
)


def get_edi_files(directory: str) -> Generator[str, None, None]:
    for file in os.listdir(directory):
        _, extension = splitext(file)

        if extension == '.edi':
            yield abspath(join(directory, file))

# Tensor de Fase
if None:
    for edi_file in get_edi_files('./mtpy-edis/'):
        edi_filename = basename(splitext(edi_file)[0])

        edi_data = MT(edi_file)
        edi_plot = edi_data.plot_mt_response(plot_num=1,
                                             plot_tipper='yri',
                                             plot_pt='y')

        # Tensor de fase
        try:
            edi_plot.save_plot(join('./plots/phase_tensor/', f'{edi_filename}_pt_plot.png' ),
                               fig_dpi=400)
        except FileNotFoundError:
            os.mkdir('./plots/phase_tensor/')

            edi_plot.save_plot(join('./plots/phase_tensor/', f'{edi_filename}_pt_plot.png' ),
                               fig_dpi=400)

        # Dimensionalidad
        dim = dimensionality(z_object=edi_data.Z,
                             skew_threshold=5,
                             eccentricity_threshold=0.1)

        # Strike angle
        strike = strike_angle(z_object=edi_data.Z,
                              skew_threshold=5,
                              eccentricity_threshold=0.1)

        with open(f'/phase_tensor/{edi_filename}_pt_data.txt', 'a') as f:
            f.write(f'Dimensionality\n{str(dim)}\nStrike Angle\n{str(strike)}\n') # A la rápida, se puede mejorar

# Strike Plot
if None:
    strike_plot = PlotStrike(fn_list=list(get_edi_files('./mtpy-edis/')),
                             fold=True,
                             plot_tipper='y',
                             show_ptphimin=True,
                             plot_type=1)

    strike_plot.save_plot('./plots/strike_plot.png',
                          file_format='png',
                          fig_dpi=400)

if None:
    for edi_file in get_edi_files('./mtpy-edis/'):
        edi_filename = basename(splitext(edi_file)[0])

        try:
            os.mkdir('./plots/pen_depth1d/')
        except FileExistsError:
            pass

        penetration_depth1d.plot_edi_file(edi_file,
                                          savefile=f'./plots/pen_depth1d/{edi_filename}_pd1d.png',
                                          fig_dpi=400)

# Penetration Depth
if None:
    period_list = [.00125,.0025, .005, .01]

    plot = penetration_depth2d.plot2Dprofile('./mtpy-edis',
                                             selected_periods=period_list,
                                             zcomponent='det',
                                             ptol=0.2,
                                             marker='o',
                                             save=True,
                                             savepath='./plots/pen_depth_profile.png')

if __name__ == '__main__':
    penetration_depth3d.plot_latlon_depth_profile('./mtpy-edis/',
                                                  10,
                                                  'det',
                                                  showfig=False,
                                                  savefig=True,
                                                  savepath='./plots/lat_lon_depth_profile.png',
                                                  fig_dpi=400)
    # Error con los periodos!?
