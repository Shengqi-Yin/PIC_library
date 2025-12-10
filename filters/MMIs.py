from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from basic.tapers import taper
from basic.waveguides import waveguide
###########################################
strip_c = PLATFORM("SOI").c # load cornerstone pdk SOI platform cband strip
rib_c = PLATFORM("SOI").rib_c

@gf.cell(check_ports=False)
def MMI(width: int|float = 6, length: int|float = 20, layer: LayerSpec = None,
        xsection: CrossSection = strip_c, n_ports:tuple[int,int] = (2, 2),
        taper_width: int|float = 1, taper_length: int|float = 10,
        taper_spacing:int|float = 2,
        waveguide_width: int|float = None,
        labels: list|str|None = None,
        label_size: int|float = 10,
        )->Component:
    # --- validation ---#
    xsection = xsection_generator(width,layer,xsection)
    if waveguide_width and waveguide_width!= xsection.width:
        raise Exception("Waveguide width not equal to xsection width, do not multiple claim the waveguide with diff info")
    max_port = max(n_ports[0],n_ports[1])
    if width <= taper_width+(max_port-1)*taper_spacing:
        raise ValueError("The sum of waveguide_spacing plus the taper exceeds the width of the MMI")
    if taper_spacing < taper_width:
        raise ValueError("The waveguides will overlap: waveguide_spacing is too small or width is too big")
    # --- layout --- #
    c = gf.Component()
    MM_block  = c.add_ref(gf.components.rectangle(size =(length,width),layer=xsection.layer))
    MM_block.dxmin,MM_block.dy = 0,0
    taper_ref = taper(width1 = xsection.width,width2=taper_width,layer=xsection.layer, length=taper_length)
    # define the input widges
    for i in range(n_ports[0]):
        input_start = (n_ports[0]-1)*taper_spacing
        widge = c.add_ref(taper_ref.copy())
        widge.dxmax,widge.dy = 0,input_start/2-i*taper_spacing
        if len(xsection.sections) == 1:
            c.add_port(name=f"o{i+1}",port = widge.ports["o1"])
    # define the output widges
    for j in range(n_ports[1]):
        output_start = (n_ports[1]-1)*taper_spacing
        widge = c.add_ref(taper_ref.copy()).mirror_x()
        widge.dxmin,widge.dy = length,output_start/2-j*taper_spacing
        if len(xsection.sections)==1:
            c.add_port(name=f"o{i+j+2}", port=widge.ports["o1"])
    # define for rib or cladding layer #
    if len(xsection.sections)>1:
        for i,section in enumerate(xsection.sections):
            if i == 0:
                r = c.get_region(layer=section.layer)
                extend_width = 0
                width_ref = section.width
            else:
                delta_width = 0.5*(section.width - width_ref)
                r = r.sized(delta_width*1000)
                c.add_polygon(r,layer=section.layer)
                extend_width = max(extend_width,delta_width)
        for i in range(n_ports[0]):
            arm = c.add_ref(waveguide(length=extend_width,xsection=xsection))
            arm.dxmax, arm.dy = -taper_length,input_start/2-i*taper_spacing
            c.add_port(name=f"o{i + 1}",port = arm.ports["o1"])
        for j in range(n_ports[1]):
            arm = c.add_ref(waveguide(length=extend_width,xsection=xsection))
            arm.dxmin, arm.dy = length+taper_length,output_start/2-j*taper_spacing
            c.add_port(name=f"o{i +j+ 2}", port=arm.ports["o2"])
    # --- add labels as annotation --- #
    if labels:
        for i,label in enumerate(labels):
            txt = c.add_ref(gf.c.text(text=f"{label}",layer=xsection.layer,size=label_size))
            txt.dx,txt.dymin = MM_block.dx, MM_block.dymax+5+(label_size+3)*i
    c.flatten()
    return c

"""
def MMI_rib(rib_width:int|float = 5.0,xsection:CrossSection = rib_c,
            labels:list|str|None = None,
            label_size:int|float = 10,
            **kwargs)->Component:
    # validation
    if xsection.sections[1] is None:
        raise ValueError("require a section define for rib layer to create the rib waveguide, expecting width and layer")
    c1 = gf.Component()
    c = gf.Component()
    c1 = MMI(xsection = xsection,labels=False, **kwargs)
    r = c1.get_region(layer=xsection.layer)
    r = r.sized(rib_width * 1000)
    core = c.add_ref(MMI(xsection = xsection, **kwargs)) # import core structure
    clad = c.add_polygon(r,layer=xsection.sections[1].layer) # import rib structure
    # --- add extension arm for external connection --- #
    for i in range(len(core.ports)):
        arm = c.add_ref(waveguide(length=rib_width,xsection=xsection).copy())
        arm.connect("o2",core.ports[f"o{i+1}"])
        c.add_port(name=f"o{i+1}",port = arm.ports["o1"])
    # --- additional label for annotations --- #
    if labels:
        for i,label in enumerate(labels):
            txt = c.add_ref(gf.c.text(text=f"{label}",layer=xsection.layer,size=label_size))
            txt.dx,txt.dymin = core.dx, core.dymax+rib_width+1+i*(label_size+3)
    c.flatten()
    return c
"""

#### be used for testing and placeholding only ####
def MMI1X2(**kwargs)->Component:
    return MMI(n_ports=(1,2),**kwargs)
def MMI2X2(**kwargs)->Component:
    return MMI(n_ports=(2,2),**kwargs)

#########################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("MMIs")
    c << MMI1X2(xsection=rib_c)
    c.show()
    c.pprint_ports()