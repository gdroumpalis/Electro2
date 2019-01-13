from enum import Enum


class RendererOperationsType(Enum):
    LivePlotting = 1
    Sampling = 2
    Handling = 3
    OfflineRendering = 4


class HandlerIndex(Enum):
    Shell = 0
    Electro = 1


class Operator(Enum):
    Greater = 0
    Lesser = 1


class ElectroAction(Enum):
    PrintMessage = 0
    Terminate = 1
