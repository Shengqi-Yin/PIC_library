from pathlib import *
from functions.env import *
from pdk.SOI220 import *
from pdk.SOI220active import *
from pdk.SOI340 import *
from pdk.SOI500 import *
from pdk.SiN300 import *
from pdk.SiN200 import *
gf.CONF.max_cellname_length=64
#####################################
SOI500 = {
    "SILICON ETCH 1 GDS 6 DARK": (6,0),
    "SILICON ETCH 2 GDS 3 LIGHT": (3,0),
    "SILICON ETCH 2 GDS 4 DARK": (4,0),
    "HEATER FILAMENTS GDS 39 LIGHT": (39,0),
    "HEATER CONTACT PADS GDS 41 LIGHT": (41,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
}

SOI340 = {
    "SILICON ETCH 1 GDS 6 DARK": (6,0),
    "SILICON ETCH 2 GDS 3 LIGHT": (3,0),
    "SILICON ETCH 2 GDS 4 DARK": (4,0),
    "SILICON ETCH 4 GDS 5 LIGHT": (5,0),
    "HEATER FILAMENTS GDS 39 LIGHT": (39,0),
    "HEATER CONTACT PADS GDS 41 LIGHT": (41,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
    "ISOLATION TRENCH GDS 46": (46,0),
}

SOI220 = {
    "SILICON ETCH 1 GDS 60 DARK": (60,0),
    "SILICON ETCH 2 GDS 6 DARK": (6,0),
    "SILICON ETCH 3 GDS 3 LIGHT": (3,0),
    "SILICON ETCH 3 GDS 4 DARK": (4,0),
    "SILICON ETCH 4 GDS 5 LIGHT": (5,0),
    "HEATER FILAMENTS GDS 39 LIGHT": (39,0),
    "HEATER CONTACT PADS GDS 41 LIGHT": (41,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
}

SOI220Active = {
    "SILICON ETCH 1 GDS 60 DARK": (60,0),
    "SILICON ETCH 2 GDS 6 DARK": (6,0),
    "SILICON ETCH 3 GDS 3 LIGHT": (3,0),
    "SILICON ETCH 3 GDS 4 DARK": (4,0),
    "SILICON ETCH 4 GDS 5 LIGHT": (5,0),
    "LOW DOSE P-TYPE GDS 7 DARK": (7,0),
    "LOW DOSE N-TYPE GDS 8 DARK": (8,0),
    "HIGH DOSE P-TYPE GDS 9 DARK": (9,0),
    "HIGH DOSE N-TYPE GDS 11 DARK": (11,0),
    "VIAS GDS 12 DARK": (12,0),
    "ELECTRODES GDS 13 LIGHT": (13,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
}

SiN300 = {
    "SIN ETCH 1 GDS 203 LIGHT": (203,0),
    "SIN ETCH 1 GDS 204 DARK": (204,0),
    "HEATER FILAMENTS GDS 39 LIGHT": (39,0),
    "HEATER CONTACT PADS GDS 41 LIGHT": (41,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
    "CLADDING OPENING GDS 22 DARK": (22,0)
}

SiN200 = {
    "SIN ETCH 1 GDS 203 LIGHT": (203,0),
    "SIN ETCH 1 GDS 204 DARK": (204,0),
    "HEATER FILAMENTS GDS 39 LIGHT": (39,0),
    "HEATER CONTACT PADS GDS 41 LIGHT": (41,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
    "CLADDING OPENING GDS 22 DARK": (22,0)
}

Ge_on_Si = {
    "BLEED AREA GDS 98":(98,0),
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
    "GERMANIUM ETCH 1 GDS 303 LIGHT": (303,0),
    "GERMANIUM ETCH 1 GDS 304 DARK": (304,0),
}

Suspened_Si = {
    "CELL OUTPLINE GDS 99": (99,0),
    "LABELS GDS 100 DARK": (100,0),
    "SUSPENDED SILICON ETCH 1 GDS 404 DARK": (404,0),
}

Layer_dictionary = {
    "SOI220": SOI220,
    "SOI340": SOI340,
    "SOI500": SOI500,
    "SOI220Active": SOI220Active,
    "SiN300": SiN300,
    "SiN200": SiN200,
    "Ge_on_Si": Ge_on_Si,
    "Suspended_Si": Suspened_Si,
}
def mono_layer_designations(
    platform: str = "SOI340",
):
    c = gf.Component()
    space = 90
    size = 70
    # for lib_name, lib in Layer_dictionary.items():
    lib_name = platform
    lib = Layer_dictionary[lib_name]
    [x_offset,y_offset,count] = [0,0,0]
    lib_name = gf.Component(lib_name)
    for name, layer in lib.items():
        lab = gf.components.text(text=name,size=size,position=(0,y_offset),layer=layer)
        y_offset -= space
        lib_name << lab
    lib_name.flatten()
    c.add_ref(lib_name).move((-lib_name.dxmin,-lib_name.dymin))
    c.flatten()
    return c
##############################################################################
SOI220_lib = {
    "Cell0_SOI220_cband_TE_Full_Packaging_Template": SOI220_cband_Full_Packaging_Template().dup(),
    "Cell0_SOI_Full_Institution": SOI220_Full_Institution().dup(),
    "Cell0_SOI_Half_Institution": SOI220_Half_Institution().dup(),
    "Heater":SOI220_heater().dup(),
    "Heater_with_isolation":SOI220_heater_with_isolation().dup(),
    "Layer_Designations": mono_layer_designations("SOI220").dup(),
    "SOI220_cband_TE_rib_GC":SOI220_cband_TE_rib_GC().dup(),
    "SOI220_cband_TE_rib_1x2_MMI":SOI220_cband_TE_rib_1x2_MMI().dup(),
    "SOI220_cband_TE_rib_2x2_MMI":SOI220_cband_TE_rib_2x2_MMI().dup(),
    "SOI220_cband_TE_rib_90deg_bend":SOI220_cband_TE_rib_90deg_bend().dup(),
    "SOI220_cband_TE_rib_crossing":SOI220_cband_TE_rib_crossing().dup(),
    "SOI220_cband_TE_rib_MM2SM_taper":SOI220_cband_TE_rib_MM2SM_taper().dup(),
    "SOI220_cband_TE_rib_MZI":SOI220_cband_TE_rib_MZI().dup(),
    "SOI220_cband_TE_strip_GC":SOI220_cband_TE_strip_GC().dup(),
    "SOI220_cband_TE_strip_apodized_GC_focusing_v1p0":SOI220_cband_TE_strip_apodized_GC_focusing_v1p0().dup(),
    "SOI220_cband_TE_strip_apodized_GC_focusing_EBL":SOI220_cband_TE_strip_apodized_GC_focusing_ebl().dup(),
    "SOI220_cband_TE_strip_1x2_MMI":SOI220_cband_TE_strip_1x2_MMI().dup(),
    "SOI220_cband_TE_strip_2x2_MMI":SOI220_cband_TE_strip_2x2_MMI().dup(),
    "SOI220_cband_TE_strip_1x2_Ysplitter":SOI220_cband_TE_strip_1x2_Ysplitter().dup(),
    "SOI220_cband_TE_strip_90deg_bend":SOI220_cband_TE_strip_90deg_bend().dup(),
    "SOI220_cband_TE_strip_crossing":SOI220_cband_TE_strip_crossing().dup(),
    "SOI220_cband_TE_strip_MM2SM_taper":SOI220_cband_TE_strip_MM2SM_taper().dup(),
    "SOI220_cband_TE_strip_MZI":SOI220_cband_TE_strip_MZI().dup(),
    "SOI220_cband_TE_rib2strip_taper":SOI220_cband_TE_rib2strip_taper().dup(),
    "SOI220_oband_TE_rib_GC":SOI220_oband_TE_rib_GC().dup(),
    "SOI220_oband_TE_rib_1x2_MMI":SOI220_oband_TE_rib_1x2_MMI().dup(),
    "SOI220_oband_TE_rib_2x2_MMI":SOI220_oband_TE_rib_2x2_MMI().dup(),
    "SOI220_oband_TE_rib_crossing":SOI220_oband_TE_rib_crossing().dup(),
    "SOI220_oband_TE_strip_GC":SOI220_oband_TE_strip_GC().dup(),
    "SOI220_oband_TE_strip_1x2_MMI":SOI220_oband_TE_strip_1x2_MMI().dup(),
    "SOI220_oband_TE_strip_2x2_MMI":SOI220_oband_TE_strip_2x2_MMI().dup(),
    "SOI220_oband_TE_strip_1x2_Ysplitter":SOI220_oband_TE_strip_1x2_Ysplitter().dup(),
    "SOI220_oband_TE_strip_90deg_bend":SOI220_oband_TE_strip_90deg_bend().dup(),
    "SOI220_oband_TE_strip_crossing":SOI220_oband_TE_strip_crossing().dup(),
}

SOI220active_lib = {
    "Cell0_SOI220_cband_TE_Full_Packaging_Template": SOI220_cband_Full_Packaging_Template().dup(),
    "Cell0_SOI_Full_Institution": SOI220_Full_Institution().dup(),
    "Cell0_SOI_Half_Institution": SOI220_Half_Institution().dup(),
    "Heater":SOI220_heater().dup(),
    "Heater_with_isolation":SOI220_heater_with_isolation().dup(),
    "Layer_Designations": mono_layer_designations("SOI220Active").dup(),
    "SOI220_cband_TE_rib_GC":SOI220_cband_TE_rib_GC().dup(),
    "SOI220_cband_TE_rib_1x2_MMI":SOI220_cband_TE_rib_1x2_MMI().dup(),
    "SOI220_cband_TE_rib_2x2_MMI":SOI220_cband_TE_rib_2x2_MMI().dup(),
    "SOI220_cband_TE_rib_90deg_bend":SOI220_cband_TE_rib_90deg_bend().dup(),
    "SOI220_cband_TE_rib_crossing":SOI220_cband_TE_rib_crossing().dup(),
    "SOI220_cband_TE_rib_MM2SM_taper":SOI220_cband_TE_rib_MM2SM_taper().dup(),
    "SOI220_cband_TE_rib_Defect_Detector":SOI220_cband_TE_rib_Defect_Detector().dup(),
    "SOI220_cband_TE_rib_MZM":SOI220_cband_TE_rib_MZM().dup(),
    "SOI220_cband_TE_strip_GC":SOI220_cband_TE_strip_GC().dup(),
    "SOI220_cband_TE_strip_apodized_GC_focusing_EBL":SOI220_cband_TE_strip_apodized_GC_focusing_ebl().dup(),
    "SOI220_cband_TE_strip_1x2_MMI":SOI220_cband_TE_strip_1x2_MMI().dup(),
    "SOI220_cband_TE_strip_2x2_MMI":SOI220_cband_TE_strip_2x2_MMI().dup(),
    "SOI220_cband_TE_strip_1x2_Ysplitter":SOI220_cband_TE_strip_1x2_Ysplitter().dup(),
    "SOI220_cband_TE_strip_90deg_bend":SOI220_cband_TE_strip_90deg_bend().dup(),
    "SOI220_cband_TE_strip_crossing":SOI220_cband_TE_strip_crossing().dup(),
    "SOI220_cband_TE_strip_MM2SM_taper":SOI220_cband_TE_strip_MM2SM_taper().dup(),
    "SOI220_cband_TE_rib2strip_taper":SOI220_cband_TE_rib2strip_taper().dup(),
    "SOI220_oband_TE_rib_GC":SOI220_oband_TE_rib_GC().dup(),
    "SOI220_oband_TE_rib_1x2_MMI":SOI220_oband_TE_rib_1x2_MMI().dup(),
    "SOI220_oband_TE_rib_2x2_MMI":SOI220_oband_TE_rib_2x2_MMI().dup(),
    "SOI220_oband_TE_rib_crossing":SOI220_oband_TE_rib_crossing().dup(),
    "SOI220_oband_TE_rib_MZM":SOI220_oband_TE_rib_MZM().dup(),
    "SOI220_oband_TE_rib_Defect_Detector":SOI220_oband_TE_rib_Defect_Detector().dup(),
    "SOI220_oband_TE_strip_1x2_MMI":SOI220_oband_TE_strip_1x2_MMI().dup(),
    "SOI220_oband_TE_strip_2x2_MMI":SOI220_oband_TE_strip_2x2_MMI().dup(),
    "SOI220_oband_TE_strip_1x2_Ysplitter":SOI220_oband_TE_strip_1x2_Ysplitter().dup(),
    "SOI220_oband_TE_strip_90deg_bend":SOI220_oband_TE_strip_90deg_bend().dup(),
    "SOI220_oband_TE_strip_crossing":SOI220_oband_TE_strip_crossing().dup(),
}

SOI340_lib = {
    "Cell0_SOI220_cband_TE_Full_Packaging_Template": SOI340_cband_Full_Packaging_Template().dup(),
    "Cell0_SOI_Full_Institution": SOI340_Full_Institution().dup(),
    "Cell0_SOI_Half_Institution": SOI340_Half_Institution().dup(),
    "Heater":SOI340_heater().dup(),
    "Heater_with_isolation":SOI340_heater_with_isolation().dup(),
    "Layer_Designations": mono_layer_designations("SOI340").dup(),
    "SOI340_cband_TE_strip_GC":SOI340_cband_TE_strip_GC().dup(),
    "SOI340_cband_TE_strip_1x2_MMI":SOI340_cband_TE_strip_1x2_MMI().dup(),
    "SOI340_cband_TE_strip_2x2_MMI":SOI340_cband_TE_strip_2x2_MMI().dup(),
    "SOI340_cband_TE_strip_MZI":SOI340_cband_TE_strip_MZI().dup(),
    "SOI340_cband_TE_strip_waveguide":SOI340_cband_TE_strip_waveguide().dup(),
    "SOI340_cband_TE_rib2strip_taper":SOI340_cband_TE_rib2strip_taper().dup(),
    "SOI340_cband_TE_rib_90deg_bend":SOI340_cband_TE_rib_90deg_bend().dup(),
    "SOI340_cband_TE_rib_waveguide":SOI340_cband_TE_rib_waveguide().dup(),
    "SOI340_oband_TE_strip_GC":SOI340_oband_TE_strip_GC().dup(),
    "SOI340_oband_TE_strip_1x2_MMI":SOI340_oband_TE_strip_1x2_MMI().dup(),
    "SOI340_oband_TE_strip_2x2_MMI":SOI340_oband_TE_strip_2x2_MMI().dup(),
    "SOI340_oband_TE_strip_waveguide":SOI340_oband_TE_strip_waveguide().dup(),
}

SOI500_lib = {
    "Cell0_SOI220_cband_TE_Full_Packaging_Template": SOI500_cband_Full_Packaging_Template().dup(),
    "Cell0_SOI_Full_Institution": SOI500_Full_Institution().dup(),
    "Cell0_SOI_Half_Institution": SOI500_Half_Institution().dup(),
    "Heater":SOI500_heater().dup(),
    "Layer_Designations": mono_layer_designations("SOI500").dup(),
    "SOI500_cband_TE_rib_GC":SOI500_cband_TE_rib_GC().dup(),
    "SOI500_cband_TE_rib_1x2_MMI":SOI500_cband_TE_rib_1x2_MMI().dup(),
    "SOI500_cband_TE_rib_2x2_MMI":SOI500_cband_TE_rib_2x2_MMI().dup(),
    "SOI500_cband_TE_rib_90deg_bend":SOI500_cband_TE_rib_90deg_bend().dup(),
    "SOI500_cband_TE_rib_waveguide":SOI500_cband_TE_rib_waveguide().dup(),
}

SiN300_lib = {
    "Cell0_SiN_Institution":SiN300_Institution().dup(),
    "Heater":SiN300_heater().dup(),
    "Layer_Designations": mono_layer_designations("SiN300").dup(),
    "SiN300_cband_TE_strip_GC":SiN300_cband_TE_strip_GC().dup(),
    "SiN300_cband_TE_strip_1x2_MMI":SiN300_cband_TE_strip_1x2_MMI().dup(),
    "SiN300_cband_TE_strip_2x2_MMI":SiN300_cband_TE_strip_2x2_MMI().dup(),
    "SiN300_cband_TE_strip_90deg_bend":SiN300_cband_TE_strip_90deg_bend().dup(),
    "SiN300_cband_TE_strip_waveguide":SiN300_cband_TE_strip_waveguide().dup(),
    "SiN300_oband_TE_strip_GC":SiN300_oband_TE_strip_GC().dup(),
    "SiN300_oband_TE_strip_1x2_MMI":SiN300_oband_TE_strip_1x2_MMI().dup(),
    "SiN300_oband_TE_strip_2x2_MMI":SiN300_oband_TE_strip_2x2_MMI().dup(),
    "SiN300_oband_TE_strip_90deg_bend":SiN300_oband_TE_strip_90deg_bend().dup(),
    "SiN300_oband_TE_strip_waveguide":SiN300_oband_TE_strip_waveguide().dup(),
}

SiN200_lib = {
    "Cell0_SiN_Institution":SiN200_Institution().dup(),
    "Heater":SiN200_heater().dup(),
    "Layer_Designations": mono_layer_designations("SiN200").dup(),
    "SiN200_780nm_TE_strip_GC":SiN200_780nm_TE_strip_GC().dup(),
    "SiN200_780nm_TE_strip_1x2_MMI":SiN200_780nm_TE_strip_1x2_MMI().dup(),
    "SiN200_780nm_TE_strip_2x2_MMI":SiN200_780nm_TE_strip_2x2_MMI().dup(),
    "SiN200_780nm_TE_strip_waveguide":SiN200_780nm_TE_strip_waveguide().dup(),
    "SiN200_638nm_TE_strip_GC":SiN200_638nm_TE_strip_GC().dup(),
    "SiN200_638nm_TE_strip_1x2_MMI":SiN200_638nm_TE_strip_1x2_MMI().dup(),
    "SiN200_638nm_TE_strip_2x2_MMI":SiN200_638nm_TE_strip_2x2_MMI().dup(),
    "SiN200_638nm_TE_strip_waveguide":SiN200_638nm_TE_strip_waveguide().dup(),
    "SiN200_520nm_TE_strip_GC":SiN200_520nm_TE_strip_GC().dup(),
    "SiN200_520nm_TE_strip_1x2_MMI":SiN200_520nm_TE_strip_1x2_MMI().dup(),
    "SiN200_520nm_TE_strip_2x2_MMI":SiN200_520nm_TE_strip_2x2_MMI().dup(),
    "SiN200_520nm_TE_strip_waveguide":SiN200_520nm_TE_strip_waveguide().dup(),
}
#####################################
if __name__ == "__main__":
    cell_lib = SiN200_lib
    for name in cell_lib.keys():
        print(f"{name} loaded")