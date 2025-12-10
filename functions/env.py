from __future__ import annotations
import os,sys
import gdsfactory as gf
from gdsfactory.component import Component, ComponentAllAngle
from gdsfactory.path import arc
from gdsfactory.snap import snap_to_grid
from gdsfactory.typings import CrossSectionSpec, LayerSpec, LayerSpecs, ComponentSpec, Layer
from gdsfactory.technology import LayerMap
from gdsfactory.cross_section import CrossSection, cross_section
from gdsfactory import Path
from functools import partial
from typing import Any, Union, List, Tuple, Literal, overload, Sequence, Type
import numpy as np
import scipy as sp
import numpy.typing as npt
from numpy import cos, sin, tan, pi, float64
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from pdk.CORNERSTONE import PLATFORM
############# Essential definition for BBs ##################
def xsection_generator(width:float|int = None,
                       layer: LayerSpec = None,
                       xsection: CrossSectionSpec = None)->CrossSection:
    """ Function to verify and package a CrossSection object."""
    if xsection:
        return xsection
    elif width and layer:
        return cross_section(width=width, layer=layer)
    else:
        raise Exception("No xsection specified, missing key params of xsection or (width and layer)")



if __name__ == "__main__":
    print(pi)