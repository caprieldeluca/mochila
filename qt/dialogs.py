# -*- coding: utf-8 -*-
from mochila import plog

from qgis.PyQt.QtCore import (
    QUrl,
    QStandardPaths
)
from qgis.PyQt.QtWidgets import (
    QFileDialog
)
from qgis.utils import iface


def restore_urls_fd():
    """ Restore sidebar urls (to useful ones) in file dialogs"""
    useful = [8, 14, 0, 1, 4, 5, 6]
    urls = ([QUrl.fromLocalFile(QStandardPaths.standardLocations(i)[0]) for i in useful])
    file_dialog = QFileDialog(iface.mainWindow())
    file_dialog.setSidebarUrls(urls)
    if file_dialog.exec_():
        filenames = file_dialog.selectedFiles()
        plog("filenames =", filenames)
    else:
        plog("File dialog cancelled")

def plog_standardpaths():
    """Log a dictionary with standardpaths enumeration"""
    locations = {}
    i = 0
    while QStandardPaths.displayName(i) is not '':
        locations[str(i)] = {
            'NAME': QStandardPaths.displayName(i),
            'PATH': QStandardPaths.standardLocations(i)}
        i += 1
    plog("locations =", locations)

