from pdk._built_in_comps import *
############################################
strip_c = PLATFORM("SOI").c
strip_o = PLATFORM("SOI").o
rib_c = PLATFORM("SOI").rib_c
rib_o = PLATFORM("SOI").rib_o
layers = PLATFORM("SOI").layers
##########################################
@gf.cell(check_ports=False)
def SOI340_cband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_c,xp=0,offset = 2.697,backend=4.168,pitch=0.59,duty=325/590,
                                 cycles=60,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI340_cband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_c,width=6,length=34.7,taper_width=1.5,taper_length=20,taper_spacing=3.15)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI340_cband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_c,width=6,length=46.5,taper_width=1.5,taper_length=20,taper_spacing=2.03)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI340_cband_TE_strip_MZI()->Component:
    c = MZI_unit(gc_ref=SOI340_cband_TE_strip_GC().copy(),splitter=SOI340_cband_TE_strip_1x2_MMI(),
                    combiner = SOI340_cband_TE_strip_2x2_MMI(), xsection=strip_c,dual_arms=False,length_y=35)
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "TOPM", "SMF28", 6.9
    return c

@gf.cell()
def SOI340_cband_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_c,length=100)
    c.info["component_type"]="waveguide"
    return c

@gf.cell(check_ports=False)
def SOI340_cband_TE_rib2strip_taper()->Component:
    c = waveguide_taper_Rib2Strip(strip_xsection = strip_c,rib_xsection = rib_c,length=200)
    c.info["component_type"] = "WaveguideConverter"
    return c

@gf.cell(check_ports=False)
def SOI340_cband_TE_rib_90deg_bend()->Component:
    c =  bend90(xsection = rib_c,radius=100)
    c.info["component_type"] = "Bend"
    return c

@gf.cell()
def SOI340_cband_TE_rib_waveguide()->Component:
    c = waveguide(xsection = rib_c,length=100)
    c.info["component_type"]="waveguide"
    return c

@gf.cell(check_ports=False)
def SOI340_oband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_o,xp=0,offset = 9.83,backend=4.168,pitch=0.47,duty=220/470,
                                 cycles=60,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI340_oband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_o,width=6,length=42.6,taper_width=1.5,taper_length=20,taper_spacing=3.1)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI340_oband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_o,width=6,length=57,taper_width=1.5,taper_length=20,taper_spacing=2.)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell()
def SOI340_oband_TE_strip_waveguide()->Component:
    c = waveguide(xsection = strip_o,length=100)
    c.info["component_type"]="waveguide"
    return c

## ==== drawing panel ===== ##
@gf.cell()
def SOI340_heater()->Component:
    return waveguide_with_heater(fil_width=2,pad_offset=80,pad_gap=20,removal_waveguide=True)

def SOI340_heater_with_isolation()->Component:
    return waveguide_with_heater(fil_width=2,pad_offset=80,pad_gap=20,removal_waveguide=True,isolation=True)

@gf.cell(check_ports=False)
def SOI340_cband_Full_Packaging_Template()->Component:
    c = die_frame_template(gc_ref=SOI340_cband_TE_strip_GC)
    c.info["component_type"],c.info["fiber_type"], c.info["coupling_angle_cladding"] = "PackagingTemplate","SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI340_Full_Institution()->Component:
    c = die_frame(type="full")
    c.ports.clear()
    return c

@gf.cell(check_ports=False)
def SOI340_Half_Institution()->Component:
    c = die_frame(type="half")
    c.ports.clear()
    return c
#########################################
##########################################
if __name__ == "__main__":
     gf.clear_cache()
     c = gf.Component("SOI500 Platform")
     c<<SOI340_heater_with_isolation()
     c.show()