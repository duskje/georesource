from resistics.project.io import newProject, loadProject
from resistics.project.spectra import calculateSpectra
from resistics.project.transfunc import processProject

from mtpy.core.edi import Header, Edi
from mtpy.core.z import Tipper, Z

from tempfile import TemporaryDirectory
from os.path import abspath, join

import os


def ats_2_edi(input: str, output: str) -> None:
    with TemporaryDirectory() as temp_dir:
        project_data = newProject(temp_dir, '2021-02-10 00:00:00')
        project_data.createSite('site')

        calculateSpectra(project_data)

        project_data.refresh()

        processProject(project_data)

        print(os.listdir(join(temp_dir, '')))

#        for dir in os.listdir()
#            print(dir)


if __name__ == '__main__':
    ats_2_edi('', '')