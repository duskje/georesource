#from resistics.project.io import newProject

from resistics.project.io import loadProject

project_data = loadProject(projectPath="./")

## NOTAS: Proyecto

if None:
    from resistics.project.io import newProject

    project_data = newProject("./", "2012-02-10 00:00:00")


    project_data.createSite("site1")

    site_data = project_data.getSiteData("site1")
    site_data.view()

## NOTAS: Función de Transferencia
if None:
    from resistics.project.spectra import calculateSpectra
    from resistics.project.transfunc import processProject

    calculateSpectra(project_data)
    project_data.refresh()

    calculateSpectra(project_data)

    processProject(project_data)

## NOTA: Tensor de Impedancia
if None:
    from resistics.project.transfunc import viewImpedance

    figs = viewImpedance(project_data,
                         sites=["site1"],
                         show=False,
                         save=False)

    figs[0].savefig("./images/view_impedance.png")

    figs = viewImpedance(project_data,
                         sites=["site1"],
                         polarisations=["ExHy", "EyHx"],
                         save=False,
                         show=False)

    figs[0].savefig("./images/view_impedance_ExHy_EyHx.png")

    figs = viewImpedance(project_data,
                         sites=["site1"],
                         oneplot=False,
                         save=False,
                         show=False)


    figs[0].savefig("./images/view_impedance_separate.png")

    from resistics.project.transfunc import getTransferFunctionData

    freqs = {512, 4096, 32768, 65536}

    for freq in freqs:
        transfunc_data = getTransferFunctionData(project_data, "site1", freq)

        fig = transfunc_data.viewImpedance(oneplot=True,
                                           save=False,
                                           show=False)

    fig.savefig(f'./images/transfunc_{freq}hz')

    from resistics.project.transfunc import processProject

    processProject(project_data,
                   site=['site1'],
                   outchans=['Ex', 'Ey', 'Hz'],
                   postpend="with_Hz")
#
## NOTAS: Tipper
if None:
    from resistics.project.transfunc import viewTipper

    fig = viewTipper(project_data,
                     sites=['site1'],
                     postpend="with_Hz",
                     save=False,
                     show=False)

    fig[0].savefig('./images/tipper_hz.png')

    fig = viewTipper(project_data,
                     sites=['site1'],
                     polarisations=["ExHy", "EyHx"],
                     postpend="with_Hz",
                     save=False,
                     show=False)

    fig[0].savefig('./images/tipper_hz_polarisations.png')

## NOTAS: Espectro

if None:
    from resistics.project.spectra import viewSpectra
    from resistics.project.spectra import viewSpectraStack
    from resistics.project.spectra import viewSpectraSection

    from os import listdir

    matching_hz = {
        'meas_2021-02-02_20-23-00': 512,
        'meas_2021-02-02_20-29-00': 4096,
        'meas_2021-02-02_20-34-00': 32768,
        'meas_2021-02-02_20-37-00': 65536,
    }

    for dir in listdir('./timeData/site1/'):
        fig = viewSpectra(project_data,
                          "site1",
                          dir,
                          show=False,
                          save=False)

        fig.savefig(f'./images/spectra_img/spectraband_{matching_hz[dir]}')

        fig = viewSpectraSection(project_data,
                                 "site1",
                                 dir,
                                 show=False,
                                 save=False)

        fig.savefig(f'./images/spectra_img/spectrasection_{matching_hz[dir]}')

        fig = viewSpectraStack(project_data,
                               "site1",
                               dir,
                               show=False,
                               save=False)

        fig.savefig(f'./images/spectra_img/spectrastack_{matching_hz[dir]}')

from os import listdir
from os.path import join, basename, splitext
import re


def get_freqs(time_data_dir: str) -> dict:
    meas_freq = {}

    for meas_dir in listdir(time_data_dir):
        for file in listdir(join(time_data_dir, meas_dir)):
            if file.endswith('.ats'):
                match = re.search(r'(?!_)[0-9]+(?=H\.ats)', file)
                meas_freq[meas_dir] = match.group(0)
                break

    return meas_freq



## NOTAS: Estadísticas
if __name__ == '__main__':
    from resistics.statistics.utils import getStatNames
    from resistics.project.statistics import calculateStatistics
    from resistics.project.statistics import getStatisticData
    from resistics.project.statistics import viewStatistic


    stats, remotestats = getStatNames()

    calculateStatistics(project_data, stats=stats)

    for meas_file, freq in get_freqs('./timeData/site1/').items():
        stats_data = getStatisticData(project_data,
                                      "site1",
                                      meas_file,
                                      "coherence",
                                      declevel=0)

        try:
            stats_data.view(0).savefig(f'./images/coherence_stats_{meas_file}_{freq}H.png')
        except AttributeError:
            pass

        fig = viewStatistic(project_data,
                            "site1",
                            freq,
                            "transferFunction",
                            ylim=[-2000, 2000])
        try:
            fig.savefig(f'./images/transfunc_stats_{meas_file}_{freq}H.png')
        except AttributeError:
            pass

