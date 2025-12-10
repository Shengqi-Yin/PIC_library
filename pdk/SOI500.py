from pdk._built_in_comps import *
############################################
rib_c = PLATFORM("SOI").c
layers = PLATFORM("SOI").layers
###########################################
### ==== online layout ==== ###
@gf.cell(check_ports=False)
def SOI500_cband_TE_rib_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = rib_c,xp=0,offset = 7.116,backend=3.334,pitch=0.53,duty=280/530,
                                 cycles=60,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI500_cband_TE_rib_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = rib_c,width=6,length=37.5,taper_width=1.6,taper_length=20,taper_spacing=3.07)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI500_cband_TE_rib_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = rib_c,width=6,length=50.2,taper_width=1.6,taper_length=20,taper_spacing=2)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI500_cband_TE_rib_90deg_bend()->Component:
    c =  bend90(xsection = rib_c,radius=25)
    c.info["component_type"] = "Bend"
    return c

@gf.cell()
def SOI500_cband_TE_rib_waveguide()->Component:
    c = waveguide(xsection = rib_c,length=100)
    c.info["component_type"]="waveguide"
    return c

## ==== drawing panel ===== ##
@gf.cell()
def SOI500_heater()->Component:
    return waveguide_with_heater(fil_width=0.6,pad_offset=80,pad_gap=20,removal_waveguide=True)

@gf.cell(check_ports=False)
def SOI500_cband_Full_Packaging_Template()->Component:
    c = die_frame_template(gc_ref=SOI500_cband_TE_rib_GC)
    c.info["component_type"],c.info["fiber_type"], c.info["coupling_angle_cladding"] = "PackagingTemplate","SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI500_Full_Institution()->Component:
    c = die_frame(type="full")
    c.ports.clear()
    return c

@gf.cell(check_ports=False)
def SOI500_Half_Institution()->Component:
    c = die_frame(type="half")
    c.ports.clear()
    return c

##########################################
if __name__ == "__main__":
     gf.clear_cache()
     c = gf.Component("SOI500 Platform")
     c<<SOI500_cbnd_TE_rib_waveguide()
     c.show()
