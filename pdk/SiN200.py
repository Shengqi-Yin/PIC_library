from pdk._built_in_comps import *
#############################
strip_780 = PLATFORM("SiN").vis780
strip_638 = PLATFORM("SiN").vis638
strip_520 = PLATFORM("SiN").vis520
layers = PLATFORM("SiN").layers
#################################
### ==== online layout ==== ###
@gf.cell()
def SiN200_780nm_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=6,xsection = strip_780,xp=0,offset = 3.594,backend=10,pitch=0.668,duty=0.5,
                                 cycles=30,taper_length=200,layer=[layers["WGN"],layers["WGP"]]).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "780HP", 12.4
    return c

@gf.cell()
def SiN200_780nm_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_780,width=4.3,length=21.6,taper_width=1.8,taper_length=40,taper_spacing=2.15)
    c.info["component_type"]="MMI1x2"
    return c

@gf.cell()
def SiN200_780nm_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_780,width=4.3,length=88,taper_width=1.8,taper_length=40,taper_spacing=2.15)
    c.info["component_type"]="MMI2x2"
    return c

@gf.cell()
def SiN200_780nm_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_780,length=100)
    c.info["component_type"]="waveguide"
    return c

@gf.cell()
def SiN200_638nm_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=5.5,xsection = strip_638,xp=0,offset = 3.538,backend=10,pitch=0.504,duty=238/504,
                                 cycles=30,taper_length=200,layer=[layers["WGN"],layers["WGP"]]).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SM600", 12.4
    return c

@gf.cell()
def SiN200_638nm_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_638,width=3.5,length=18.4,taper_width=1.4,taper_length=40,taper_spacing=1.75)
    c.info["component_type"]="MMI1x2"
    return c

@gf.cell()
def SiN200_638nm_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_638,width=3.5,length=73.2,taper_width=1.4,taper_length=40,taper_spacing=1.75)
    c.info["component_type"]="MMI2x2"
    return c

@gf.cell()
def SiN200_638nm_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_638,length=100)
    c.info["component_type"]="waveguide"
    return c

@gf.cell()
def SiN200_520nm_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=5,xsection = strip_520,xp=0,offset = 5.035,backend=5,pitch=0.417,duty=208/417,
                                 cycles=30,taper_length=200,layer=[layers["WGN"],layers["WGP"]]).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SM400", 15.1
    return c

@gf.cell()
def SiN200_520nm_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_520,width=3.4,length=21.6,taper_width=1.3,taper_length=40,taper_spacing=1.7)
    c.info["component_type"]="MMI1x2"
    return c

@gf.cell()
def SiN200_520nm_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_520,width=3.4,length=84.8,taper_width=1.3,taper_length=40,taper_spacing=1.7)
    c.info["component_type"]="MMI2x2"
    return c

@gf.cell()
def SiN200_520nm_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_520,length=100)
    c.info["component_type"]="waveguide"
    return c
### ==== drawing panel ==== ###
@gf.cell()
def SiN200_Institution()->Component:
    c = die_frame(type="quadrant")
    c.ports.clear()
    return c

@gf.cell()
def SiN200_heater()->Component:
    return waveguide_with_heater(fil_width=2,pad_offset=80,pad_gap=20,removal_waveguide=True)
#################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("SiN220_platform")
    c <<SiN200_520nm_TE_strip_waveguide()
    c.show()