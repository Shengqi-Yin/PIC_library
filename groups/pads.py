from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from basic.tapers import ramp, taper
#################################################
layers = PLATFORM("SOI").layers

@gf.cell
def pad(size: tuple[int|float]= (150,200),
        layer: LayerSpec = layers["PAD"],
        ports: list[str]|str = "e4",
        port_width: int|float = None,
        **kwargs)->Component:
    c = gf.Component()
    if isinstance(ports, str):
        ports = [ports]
    c.add_ref(gf.components.rectangle(size=size, layer=layer,centered=True))
    port_lib = {
        "e1":{"width":size[1],"orientation":180,"center":(-0.5*size[0],0)},
        "e2": {"width": size[0], "orientation": 90, "center": (0,0.5 * size[1])},
        "e3": {"width": size[1], "orientation": 0, "center": (0.5 * size[0],0)},
        "e4": {"width": size[0], "orientation": -90, "center": (0,-0.5 * size[1])},
    }
    for port in ports:
        port_width = port_lib[port]["width"] if port_width is None else port_width
        c.add_port(name=port,orientation=port_lib[port]["orientation"],width=port_width,
                   center=port_lib[port]["center"],layer=layer,port_type="pad")
    # c.flatten()
    return c

@gf.cell
def pad_GSGSG(pitch:int|float = 100,
              extend_connection: bool = True,
              extend_length: int|float = 99,
              extend_width: int|float = 9.1,
              extend_gap: int|float = 4,
              dummy_mode: bool = True, # for wide wire connection in MZI
              **kwargs)->Component:
    # --- transfer data from top level --- #
    size = kwargs.get("size",(69,75))
    layer = kwargs.get("layer",layers["PAD"])
    # --- layout --- #
    c = gf.Component()
    for i in range(5):
        # add pads
        unit = c.add_ref(pad(size = size,**kwargs))
        unit.dx, unit.dymax = (i-2)*pitch, 0
        # add extension arms for internal connection
        if extend_connection:
            if i in (1,3): # add source port
                x1 = cross_section(width = unit.dxsize,layer=layer,port_names=["e1","e2"],port_types=["pad","pad"])
                x2 = cross_section(width = extend_width,layer=layer,port_names=["e1","e2"],port_types=["electrical_rf","electrical_rf"])
                xtrans = gf.path.transition(cross_section1=x1,cross_section2=x2,width_type="linear") # define a transition xsection
                p1 = gf.path.straight(length=extend_length,npoints=2)
                transition = c.add_ref(gf.path.extrude_transition(p1,xtrans))# define the shape of transition in taper
            elif i in (0,4): # add side ground port
                transition = c.add_ref(ramp(width1=unit.dxsize, width2=pitch+unit.dxsize/2-extend_width/2-extend_gap,length=extend_length,
                         layer=layer,port_type = "electrical_rf" )) # define the shape of transition in ramp
                if i == 4:
                    transition = transition.mirror_x()
            elif i == 2: # add central ground port
                transition = c.add_ref(taper(width1=unit.dxsize, width2=pitch*2-extend_width-extend_gap*2,
                         length=extend_length,layer=layer, port_type="electrical_rf")) # define the shape of transition in taper
            transition.connect("e1",unit.ports["e4"],allow_type_mismatch=True)
            # add ports from extension region
            c.add_port(name = f"e{i+1}",port = transition.ports["e2"])
        else: # add ports from pad info
            c.add_port(name = f"e{i+1}",port = unit.ports["e4"],port_type="electrical_rf")
    # add global pad
    c.add_port(name="pad1", width=pitch * 4 + unit.dxsize, orientation=90, layer=layer, center=(0, 0), port_type="pad_rf")
    # add dummy pad
    if dummy_mode:
        for i in range(4):
            c.add_port(name= f"d{i+1}", width = extend_gap, orientation=-90,layer=(1013,0),port_type="pad_rf",
                       center=(c.ports[f"e{2*(i//2+1)}"].dx+(2*(i%2-0.5))*(extend_width/2+extend_gap/2),c.ports["e2"].dy))
    c.flatten()
    return c


#####################################################
@gf.cell # for single pad only, for those multiport pad cannot transfer port info correct
def pad_array(pad_ref = pad,
              period: int|float = 300,
              n_cols: int = 31,
              n_rows: int = None,
              count_from: int = 1,
              short_name: bool = True,
              **kwargs)->Component:
    # validate
    if n_cols is None:
        n_cols = 1
    if n_rows is None:
        n_rows = 1
    c = gf.Component()
    for j in range(n_rows):
        for i in range(n_cols):
            pad_unit = c.add_ref(pad_ref(**kwargs))
            pad_unit.move((i*period,j*period))
            for port in pad_unit.ports:
                if len(pad_unit.ports)==1 and short_name:
                    c.add_port(name=f"e{i + j + count_from}", port=port)
                else:
                    c.add_port(name=f"e{i+j+count_from}_{str(port.name)[-1]}",port=port)
    c.flatten()
    return c


###############################
if __name__ =="__main__":
    gf.clear_cache()
    c = gf.Component("pads")
    c <<pad_GSGSG(layer=layers["ELC"])
    c.show()