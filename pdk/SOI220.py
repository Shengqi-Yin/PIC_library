from pdk._built_in_comps import *
##############################################################
### ==== Cross-Sections & LayerMaps ==== ###
strip_c = PLATFORM("SOI").c
rib_c = PLATFORM("SOI").rib_c
strip_o = PLATFORM("SOI").o
rib_o = PLATFORM("SOI").rib_o
layers = PLATFORM("SOI").layers
##############################################################
### ==== online layout ==== ###
@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = rib_c,xp=0,offset = 0.342,backend=4.173,pitch=0.63,duty=0.5,
                                 cycles=60,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = rib_c,width=6,length=32.7,taper_width=1.5,taper_length=20,taper_spacing=3.14)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = rib_c,width=6,length=44.8,taper_width=1.5,taper_length=20,taper_spacing=2.3)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_90deg_bend()->Component:
    c =  bend90(xsection = rib_c,radius=25)
    c.info["component_type"] = "Bend"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_crossing()->Component:
    pts = [rib_c.width,0.8,0.904,1.4,1.344,1.316,1.308,1.4,1.45,1.65,1.65,1.65,rib_c.width]
    c = crossing(xsection = rib_c,box=9.24,segments = pts)
    c.info["component_type"] = "Crossing"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_MM2SM_taper()->Component:
    c = waveguide_taper(xsection = rib_c,width2=10,length=450).copy().mirror_x(225)
    c.info["component_type"] = "Taper"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib_MZI()->Component:
    c = MZI_unit(gc_ref=SOI220_cband_TE_rib_GC().copy(),splitter=SOI220_cband_TE_rib_1x2_MMI(),
                    combiner = SOI220_cband_TE_rib_2x2_MMI(), xsection=rib_c,dual_arms=False,length_y=35)
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "TOPM", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_c,xp=0,offset = 0.342,backend=4.173,pitch=0.63,duty=0.5,
                                 cycles=60,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(tags=["SOI220","Apodized","v1p0"])
def SOI220_cband_TE_strip_apodized_GC_focusing_v1p0(**kwargs)->Component:
    pos=[0, 0.731, 1.402, 2.097, 3.097, 3.735, 4.411, 5.017, 5.567, 6.717, 7.394, 7.986, 8.605, 9.223, 9.822, 10.446, 11.05, 11.647, 12.258, 12.869, 13.48, 14.087, 14.693, 15.313, 15.908, 16.513, 17.115, 17.771, 18.491, 19.248, 20.01, 20.779, 21.554, 22.34, 23.139, 23.961, 24.803, 25.66, 26.525, 27.396, 28.273, 29.157, 30.049, 30.954, 31.874, 32.81, 33.763, 34.731, 35.713, 36.711]
    tooth=[0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.335, 0.312, 0.2, 0.254, 0.246, 0.231, 0.25, 0.226, 0.231, 0.245, 0.246, 0.244, 0.24, 0.236, 0.238, 0.226, 0.24, 0.237, 0.291, 0.338, 0.37, 0.378, 0.389, 0.399, 0.411, 0.424, 0.441, 0.458, 0.473, 0.484, 0.495, 0.505, 0.516, 0.527, 0.54, 0.555, 0.571, 0.587, 0.602, 0.617, 0.632, 0.647]
    c = grating_coupler_array(ap=10, bp=10, taper_angle=28, offset=25, backend=5, xsection=strip_c,
                              tooth=tooth, pos=pos, layer=[layers["WGP"], layers["GRA"]], hyperbola=1,**kwargs).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28", 6.9
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_apodized_GC_focusing_ebl(**kwargs)->Component:
    tooth =[0.06,0.071,0.082,0.092,0.103,0.113,0.124,0.135,0.146,0.158,0.169,0.18,0.192,0.203,0.215,0.227,0.239,0.25,0.262,0.275,0.288,0.3,0.313,0.325]
    pos = [0, 0.607, 1.217, 1.829, 2.442, 3.057, 3.674, 4.293, 4.914, 5.537, 6.162, 6.789, 7.418, 8.049, 8.682, 9.317, 9.954, 10.594, 11.236, 11.879, 12.525, 13.174, 13.824, 14.477]
    c =  grating_coupler_array(ap=18.4,bp=18.4,taper_angle=38,offset = 17.7, backend=10.315,xsection=strip_c,
                        tooth=tooth,pos=pos,layer=[layers["WGP"],layers["APO"]],hyperbola=1.15,**kwargs).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"],c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_c,width=6,length=31.8,taper_width=1.5,taper_length=20,taper_spacing=3.14)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_c,width=6,length=42.5,taper_width=1.5,taper_length=20,taper_spacing=2.3)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_1x2_Ysplitter()->Component:
    c = y_splitter(xsection=strip_c,offset_x = 40, offset_y=20)
    c.info["component_type"] = "Waveguide"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_90deg_bend()->Component:
    c = bend90(xsection = strip_c,radius=5)
    c.info["component_type"] = "Bend"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_crossing()->Component:
    pts = [strip_c.width,0.438,0.6,1.2,1.334,1.37,1.418,1.6,1.588,1.848,1.848,1.848,strip_c.width]
    c = crossing(xsection = strip_c,box=9.24,segments = pts)
    c.info["component_type"] = "Crossing"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_MM2SM_taper()->Component:
    c = waveguide_taper(xsection = strip_c,width2=10,length=450).copy().mirror_x(225)
    c.info["component_type"] = "Taper"
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_strip_MZI()->Component:
    c = MZI_unit(gc_ref=SOI220_cband_TE_strip_GC().copy(),splitter=SOI220_cband_TE_strip_1x2_MMI(),
                    combiner = SOI220_cband_TE_strip_2x2_MMI(), xsection=strip_c,dual_arms=False,length_y=35)
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "TOPM", "SMF28", 6.9
    return c

@gf.cell(check_ports=False)
def SOI220_cband_TE_rib2strip_taper()->Component:
    c = waveguide_taper_Rib2Strip(strip_xsection = strip_c,rib_xsection = rib_c,length=50)
    c.info["component_type"] = "WaveguideConverter"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_rib_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = rib_o,xp=0,offset = 0.342,backend=4.173,pitch=0.5,duty=0.5,
                                 cycles=80,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_rib_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = rib_o,width=6,length=40.8,taper_width=1.5,taper_length=20,taper_spacing=3.05)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_rib_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = rib_o,width=6,length=55,taper_width=1.5,taper_length=20,taper_spacing=2.3)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_rib_crossing()->Component:
    pts = [rib_o.width,0.72,1.0,1.19,1.206,1.2,1.378,1.456,1.45,1.65,1.65,1.65,rib_o.width]
    c = crossing(xsection = rib_o,box=9.24,segments = pts)
    c.info["component_type"] = "Crossing"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_GC()->Component:
    c = grating_coupler_array(lp=10,xsection = strip_o,xp=0,offset = 0.342,backend=4.173,pitch=0.5,duty=0.5,
                                 cycles=80,taper_length=350).copy().mirror_x()
    c.info["component_type"], c.info["fiber_type"], c.info["coupling_angle_cladding"] = "GratingCoupler1D", "SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_1x2_MMI()->Component:
    c = MMI(n_ports=(1,2),xsection = strip_o,width=6,length=40.1,taper_width=1.5,taper_length=20,taper_spacing=3.05)
    c.info["component_type"] = "MMI1x2"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_2x2_MMI()->Component:
    c = MMI(n_ports=(2,2),xsection = strip_o,width=6,length=53.5,taper_width=1.5,taper_length=20,taper_spacing=2.3)
    c.info["component_type"] = "MMI2x2"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_1x2_Ysplitter()->Component:
    c = y_splitter(xsection=strip_o,offset_x = 40, offset_y=20)
    c.info["component_type"] = "Waveguide"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_90deg_bend()->Component:
    c = bend90(xsection = strip_o,radius=5)
    c.info["component_type"] = "Bend"
    return c

@gf.cell(check_ports=False)
def SOI220_oband_TE_strip_crossing()->Component:
    pts = [strip_o.width,0.6,1.2,1.168,1.168,1.306,1.428,1.7,1.926,1.926,strip_o.width]
    c = crossing(xsection = strip_o,box=8.47,segments = pts)
    c.info["component_type"] = "Crossing"
    return c

## ==== drawing panel ===== ##
@gf.cell()
def SOI220_heater()->Component:
    return waveguide_with_heater(fil_width=2,pad_offset=80,pad_gap=20,removal_waveguide=True)

def SOI220_heater_with_isolation()->Component:
    return waveguide_with_heater(fil_width=2,pad_offset=80,pad_gap=20,removal_waveguide=True,isolation=True)

@gf.cell(check_ports=False)
def SOI220_cband_Full_Packaging_Template()->Component:
    c = die_frame_template(gc_ref=SOI220_cband_TE_strip_GC)
    c.info["component_type"],c.info["fiber_type"], c.info["coupling_angle_cladding"] = "PackagingTemplate","SMF28",6.9
    return c

@gf.cell(check_ports=False)
def SOI220_Full_Institution()->Component:
    c = die_frame(type="full")
    c.ports.clear()
    return c

@gf.cell(check_ports=False)
def SOI220_Half_Institution()->Component:
    c = die_frame(type="half")
    c.ports.clear()
    return c

######################################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("SOI220_Platform_Components")
    c <<SOI220_cband_TE_strip_apodized_GC_focusing_v1p0().copy()
    # print(SOI_Full_Institution().ports)
    c.show()