from pdk._built_in_comps import *
from pdk.SOI220 import *
##############################################################
### ==== Cross-Sections & LayerMaps ==== ###
strip_c = PLATFORM("SOI").c
rib_c = PLATFORM("SOI").rib_c
rib_c_pn = PLATFORM("SOI").rib_c_pn
rib_c_pin = PLATFORM("SOI").rib_c_pin
strip_o = PLATFORM("SOI").o
rib_o = PLATFORM("SOI").rib_o
rib_o_pn = PLATFORM("SOI").rib_o_pn
rib_o_pin = PLATFORM("SOI").rib_o_pin
layers = PLATFORM("SOI").layers
#################################################################
@gf.cell()
def SOI220_cband_TE_rib_Defect_Detector()->Component:
    c = defect_detector(xsection = rib_c, doped_xsection = rib_c_pin, length = 1500,gc_ref = SOI220_cband_TE_rib_GC())
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "EOPM", "SMF28", 6.9
    return c

@gf.cell()
def SOI220_cband_TE_rib_MZM()->Component:
    c = MZI_doped_unit(xsection = rib_c, doped_xsection = rib_c_pn, gc_ref = SOI220_cband_TE_rib_GC(),
                       splitter=SOI220_cband_TE_strip_1x2_MMI(),combiner=SOI220_cband_TE_strip_2x2_MMI())
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "EOPM", "SMF28", 6.9
    return c

@gf.cell()
def SOI220_oband_TE_rib_Defect_Detector()->Component:
    c = defect_detector(xsection = rib_o, doped_xsection = rib_o_pin, length = 1500,gc_ref = SOI220_oband_TE_rib_GC())
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "EOPM", "SMF28", 6.9
    return c

@gf.cell()
def SOI220_oband_TE_rib_MZM()->Component:
    c = MZI_doped_unit(xsection = rib_o, doped_xsection = rib_o_pn, gc_ref = SOI220_oband_TE_rib_GC(),
                       splitter=SOI220_oband_TE_strip_1x2_MMI(),combiner=SOI220_oband_TE_strip_2x2_MMI())
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "EOPM", "SMF28", 6.9
    return c


#################################################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("SOI220active")
    c << SOI220_oband_TE_rib_Defect_Detector()
    c.show()