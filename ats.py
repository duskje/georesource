from resistics.time.reader_ats import TimeReader
from resistics.time.writer_ascii import TimeWriterAscii

from resistics.time.filter import lowPass, bandPass

import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from copy import deepcopy


class TimeReaderATS(TimeReader):
    def setParameters(self) -> None:
        """Set data reader parameters for ATS files"""
        self.headerF = glob.glob(os.path.join(self.dataPath, "*.xml"))
        self.dataF = glob.glob(os.path.join(self.dataPath, "*.ats"))
        self.dataByteOffset = 1024
        self.dataByteSize = 4


    def dataHeaders(self):
        """Return the data headers in the internal file format

        Returns
        -------
        recordingHeaders : List[str]
            Headers with information about the recording
        globalHeaders : List[str]
            Common headers with information about the recording
        channelHeadersInput : List[str]
            Channel setup headers
        channelHeadersOutput : List[str]
            Channel recording headers
        """
        recordingHeaders = ["start_time", "start_date", "stop_time", "stop_date"]
        globalHeaders = ["meas_channels", "sample_freq"]
        channelHeadersInput = ["gain_stage1", "gain_stage2", "hchopper", "echopper"]
        channelHeadersOutput = [
            "start_time",
            "start_date",
            "sample_freq",
            "num_samples",
            "ats_data_file",
            "sensor_type",
            "channel_type",
            "ts_lsb",
            "pos_x1",
            "pos_x2",
            "pos_y1",
            "pos_y2",
            "pos_z1",
            "pos_z2",
            "sensor_sernum",
        ]
        return (
            recordingHeaders,
            globalHeaders,
            channelHeadersInput,
            channelHeadersOutput,
        )

    def readHeader(self):
        """Read time data header file for ATS format

        Headers for ATS files are XML formatted.
        """
        if len(self.headerF) > 1:
            self.printWarning(
                "More xml files than expected. Using: {}".format(self.headerF[0])
            )
        tree = ET.parse(self.headerF[0])
        root = tree.getroot()
        # get header names
        rHeaders, gHeaders, cHeadersInput, cHeadersOutput = self.dataHeaders()

        # get recording headers
        self.headers = {}
        recording = root.find("./recording")

        for rH in rHeaders:
            self.headers[rH] = recording.find(rH).text
        # get global config headers
        globalConfig = recording.find("./input/Hardware/global_config")

        for gH in gHeaders:
            self.headers[gH] = globalConfig.find(gH).text

        # get the channel headers in the input section
        self.chanHeaders = []
        for chan in root.findall(
                "./recording/input/Hardware/channel_config/channel"
        ):
            chanH = {}
            for cH in cHeadersInput:
                chanH[cH] = chan.find(cH).text
            self.chanHeaders.append(chanH)

        # get the channel headers in the ATSWriter section of the output
        try:
            recordingOutput = recording.find("output")
            atsWriter = recordingOutput.find(".//ATSWriter")
            outputSec = atsWriter.findall("configuration/channel")
        except:
            self.printError(
                "ATSWriter section not found or channel information not found in ATSWriter"
            )
        if len(outputSec) == 0:
            self.printError(
                "No channels found in the ATSWriter. Unable to fully construct channel headers. Exiting.",
                quitrun=True,
            )
        for chan, chanH in zip(outputSec, self.chanHeaders):
            for cH in cHeadersOutput:
                chanH[cH] = chan.find(cH).text

        # a couple of things to do: add microseconds to the times
        # remember, the actual end time is one sample back
        # if you do a calculation with the number of samples and the start time
        self.headers["start_time"] = self.headers["start_time"] + ".000000"
        self.headers["stop_time"] = self.headers["stop_time"] + ".000000"
        for chanH in self.chanHeaders:
            chanH["start_time"] = chanH["start_time"] + ".000000"

        # set the lsb applied header in chans
        # for ats files, this is not applied in the raw data files
        for idx, ch in enumerate(self.chanHeaders):
            self.chanHeaders[idx]["scaling_applied"] = False
            self.chanHeaders[idx]["ts_lsb"] = "-{}".format(
                self.chanHeaders[idx]["ts_lsb"]
            )


class MetronixTimeSeries:
    default_format = {}

    def __init__(self, sample_data=None, plot_format=None):
        self.plot_format: dict = self.default_format if plot_format is None else plot_format

        if sample_data is None:
            raise ValueError
        else:
            self.sample_data = sample_data

        self.physical_data = sample_data.getPhysicalData

    @classmethod
    def from_ats(cls, data_path, plot_format=None):
        header_data = TimeReaderATS(data_path)

        return cls(header_data, plot_format)

    def filter(self, filter_type, cutoff_freq, copy=True) -> 'MetronixTimeSeries':
        if filter_type not in {'low_pass', 'band_pass'}:
            raise ValueError

        if copy:
            instance = deepcopy(self)
        else:
            instance = self

        if filter_type == 'low_pass':
            instance.physical_data = lowPass(self.physical_data, cutoff_freq, inplace=True)
        elif filter_type == 'band_pass':
            instance.physical_data = bandPass(self.physical_data, cutoff_freq, cutoff_freq, inplace=True)

        return instance

    def view_data(self, sample_start=None, sample_stop=None):
        if sample_start is None or sample_stop is None:
            # TODO: Cambiar esto
            sample_start = 0
            sample_stop = 2000

        fig = plt.figure(figsize=(16, 3 * self.sample_data.numChans))

        self.sample_data.getPhysicalData.view(fig=fig,
                                              sampleStart=sample_start,
                                              sampleStop=sample_stop)

        # Solo es padding
        fig.tight_layout(rect=[0, 0.04, 1, 0.96])
        plt.show()

    def to_ascii(self, save_path=None):
        writer = TimeWriterAscii()
        writer.outPath = save_path if save_path is not None else './'
        
        writer.writeDataset(self.sample_data, physical=True)


if __name__ == '__main__':
#    reader = TimeReaderATS('/home/duskje/PycharmProjects/georesource/drafts/birrp/ats_data/meas_2021-02-02_20-23-00')
#    unscaled_data = reader.getPhysicalData()
#
#    fig = plt.figure(figsize=(16, 3 * unscaled_data.numChans))
#    unscaled_data.view(fig=fig, sampleStop=2000)
#
#    # Padding
#    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
#
#    plt.show()
# ASCII
#    mts = MetronixTimeSeries.from_ats('/home/duskje/PycharmProjects/georesource/drafts/birrp/ats_data/meas_2021-02-02_20-23-00')
#    write = TimeWriterAscii()
#    write.outPath = '.'
#    write.writeDataFiles(mts.sample_data.chans, mts.sample_data)
    mts = MetronixTimeSeries.from_ats('/home/duskje/PycharmProjects/georesource/drafts/birrp/ats_data/meas_2021-02-02_20-23-00')
    mts.view_data()
