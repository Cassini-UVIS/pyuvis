import numpy as np
from pds.core.common import open_pds
from pds.core.parser import Parser
import os


def get_labels(fname):
    parser = Parser()
    return parser.parse(open_pds(fname))


class QUBE(object):
    def __init__(self, fname):
        self.file_id = os.path.splitext(fname)[0]
        self.label_fname = self.file_id + '.LBL'
        self.data_fname = self.file_id + '.DAT'
        self.data1D = (np.fromfile(self.data_fname, '>H')).astype(np.uint16)
        self.labels = get_labels(self.label_fname)
        self.shape = eval(self.labels['QUBE']['CORE_ITEMS'])
        self.data = self.data1D.reshape(self.shape, order='F')
