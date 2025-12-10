from pdk._built_in_comps import *
#############################################################
### ==== Cross-Sections & LayerMaps ==== ###
strip_c = PLATFORM("SiN").c
strip_o = PLATFORM("SiN").o
layers = PLATFORM("SiN").layers
###########################################
### ==== online layout ==== ###
@gf.cell()
def SiN300_cband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_c,xp=0,offset = 0.342,backend=4.173,pitch=1.32,duty_cycle=0.5,
                                 cycles=30,taper_length=200,layer=[layers["WGN"],layers["WGP"]]).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28", 13.7
    return c

@gf.cell()
def SiN300_cband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_c,width=12,length=64.7,taper_width=5.5,taper_length=50,taper_spacing=5.8)
    c.info["component_type"]="MMI1x2"
    return c

@gf.cell()
def SiN300_cband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_c,width=18,length=232,taper_width=4.5,taper_length=50,taper_spacing=6.1)
    c.info["component_type"]="MMI2x2"
    return c

@gf.cell()
def SiN300_cband_TE_strip_90deg_bend()->Component:
    c = bend90(xsection = strip_c,radius=80)
    c.info["component_type"]="bend"
    return c

@gf.cell()
def SiN300_cband_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_c,length=100)
    c.info["component_type"]="waveguide"
    return c

@gf.cell()
def SiN300_oband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_o,xp=0,offset = 0.342,backend=4.173,pitch=0.964,duty_cycle=0.5,
                                 cycles=30,taper_length=200,layer=[layers["WGN"],layers["WGP"]]).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28", 6.9
    return c
@gf.cell()
def SiN300_oband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_o,width=8,length=42,taper_width=3.5,taper_length=30,taper_spacing=4)
    c.info["component_type"]="MMI1x2"
    return c

@gf.cell()
def SiN300_oband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_o,width=12,length=126,taper_width=3.5,taper_length=30,taper_spacing=4.2)
    c.info["component_type"]="MMI2x2"
    return c

@gf.cell()
def SiN300_oband_TE_strip_90deg_bend()->Component:
    c = bend90(xsection = strip_o,radius=60)
    c.info["component_type"]="bend"
    return c

@gf.cell()
def SiN300_oband_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_o,length=100)
    c.info["component_type"]="waveguide"
    return c
### ==== drawing panel ==== ###
@gf.cell()
def SiN300_Institution()->Component:
    c = die_frame(type="quadrant")
    c.ports.clear()
    return c

@gf.cell()
def SiN300_heater()->Component:
    return waveguide_with_heater(fil_width=0.9,pad_offset=80,pad_gap=20,removal_waveguide=True)

######################################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("quadrant")
    c << SiN300_heater()
    c.show()