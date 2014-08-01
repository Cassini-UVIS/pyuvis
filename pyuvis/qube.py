import numpy as np
from pds.core.common import open_pds
from pds.core.parser import Parser
import os


def get_labels(fname):
    parser = Parser()
    return parser.parse(open_pds(fname))


class QUBE(object):
    def __init__(self, fname):
        # file management
        self.file_id = os.path.splitext(fname)[0]
        self.label_fname = self.file_id + '.LBL'
        self.data_fname = self.file_id + '.DAT'

        # read the data
        self.data1D = (np.fromfile(self.data_fname, '>H')).astype(np.uint16)

        # label stuff
        self.labels = get_labels(self.label_fname)
        self.LINE_BIN = self.labels['LINE_BIN']
        self.BAND_BIN = self.labels['BAND_BIN']
        self.shape = eval(self.labels['QUBE']['CORE_ITEMS'])
        self.line_range = (self.labels['UL_CORNER_LINE'],
                           self.labels['LR_CORNER_LINE'])
        self.band_range = (self.labels['UL_CORNER_BAND'],
                           self.labels['LR_CORNER_BAND'])

        # reshape the data with infos from label
        self.data = self.data1D.reshape(self.shape, order='F')
