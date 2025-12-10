from filters.MMIs import MMI1X2
from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic","coupler","filters","MMIs"])
from functions.env import *
from filters.MZIs import *
from basic.tapers import *
from groups.pads import pad_GSGSG, pad
###############################################
strip_c = PLATFORM("SOI").c
rib_c_pn = PLATFORM("SOI").rib_c_pn
rib_c_pin = PLATFORM("SOI").rib_c_pin
layers = PLATFORM("SOI").layers

###################################################################
### Mach-Zehnder Interferometer/ Modulator utilities ##############
###################################################################
@gf.cell(check_ports=False)
def MZI_doped_unit(mzi_ref=MZI,
                   bbox_size: tuple[int|float] = (2459,421),
                   pad_layer: LayerSpec=layers["ELC"],
                   inside_slot: int|float = 10,
                   xsection: CrossSectionSpec = None,
                   doped_xsection: CrossSectionSpec = rib_c_pn,
                   gc_ref=GC_std,
                   length_x: int|float = 1500,
                   length_y: int|float = 10,
                   delta_length: int|float = 160,
                   radius: int|float = 30,
                   dummy_gap_feature: list[int|float] = [4, 7.8, 9.1, 22, 4],
                   **kwargs,
                   )->Component:
    # --- load basic components --- #
    c = gf.Component()
    if isinstance(gc_ref,Component):
        gc_in = c.add_ref(gc_ref).mirror_x()
        gc_out1 = c.add_ref(gc_ref)
        gc_out2 = c.add_ref(gc_ref)
    else:
        gc_in = c.add_ref(gc_ref(xsection=xsection,**kwargs)).mirror_x()
        gc_out1 = c.add_ref(gc_ref(xsection=xsection, **kwargs))
        gc_out2 = c.add_ref(gc_ref(xsection=xsection, **kwargs))
    # --- validation --- #
    # x_offset = radius * 4 + length_x
    if length_x<gc_in.dxsize+radius*2+10:
        length_x = gc_in.dxsize+radius*2+10
        gf.logger.warning(f"length x is less than the safety length, automatic correct it to {length_x} um")
    if length_y<127+60-radius*4-delta_length/2:
        length_y = 127+60-radius*4-delta_length/2
        gf.logger.warning(f"length y is less than the safety length, automatic correct it to {length_y} um")
    # --- load MZI block --- #
    block = c.add_ref(MZI(doped_xsection = doped_xsection,via_width=5,radius=radius, length_heater=length_x, length_y=length_y,
                              delta_length=delta_length,dummy_gap_feature=dummy_gap_feature,xsection=xsection, **kwargs).copy())

    ## ==== start solving electrical part ==== ##
    # --- dummy Components for building block --- #
    dummy_layer=(1013,0)
    dummy_pad, dummy_base, dummy_slot, dummy_path = gf.Component(), gf.Component(), gf.Component(), gf.Component()
    pad = dummy_pad.add_ref(pad_GSGSG(layer=pad_layer,extend_width=dummy_gap_feature[3]))
    slot_size = (pad.dxsize,inside_slot) # get pad size as reference
    bbox = dummy_base.add_ref(gf.components.rectangle(size = bbox_size,layer = pad_layer))
    bbox.dx, bbox.dy = block.dx, block.dy
    slot_in1, slot_in2 = dummy_slot.add_ref(gf.components.rectangle(size = slot_size, layer = pad_layer)), dummy_slot.add_ref(gf.components.rectangle(size = slot_size, layer = pad_layer))
    slot_in1.dxmax, slot_in1.dymax = bbox.dxmax, bbox.dymax
    slot_in2.dxmin, slot_in2.dymin = bbox.dxmin, bbox.dymin
    # --- combine dummy layer for connection #
    dummy = gf.Component()
    bbox_out = dummy.add_ref(gf.boolean(A = dummy_base, B= dummy_slot, operation="A-B",layer = pad_layer))
    pad1 = dummy.add_ref(pad_GSGSG(layer=pad_layer, extend_width=dummy_gap_feature[3]))
    pad2 = dummy.add_ref(pad_GSGSG(layer=pad_layer, extend_width=dummy_gap_feature[3])).mirror_y()
    pad1.dxmax, pad1.dymin = bbox.dxmax, bbox.dymax - inside_slot
    pad2.dxmin, pad2.dymax = bbox.dxmin, bbox.dymin + inside_slot
        # create port lists and connect pads and mzi ports #
    block_ports_left = [block.ports["d1_1"],block.ports["d1_3"],block.ports["d2_1"],block.ports["d2_3"]]
    block_ports_right = [block.ports["d1_2"],block.ports["d1_4"],block.ports["d2_2"],block.ports["d2_4"]]
    pad_ports_top = [pad1.ports["d1"],pad1.ports["d2"],pad1.ports["d3"],pad1.ports["d4"]]
    pad_ports_bot = [pad2.ports["d1"],pad2.ports["d2"],pad2.ports["d3"],pad2.ports["d4"]]
    gf.routing.route_bundle(dummy_path,block_ports_right,pad_ports_top,layer = dummy_layer,
                            radius=radius,route_width=dummy_gap_feature[4],)
    gf.routing.route_bundle(dummy_path, block_ports_left, pad_ports_bot, layer=dummy_layer,
                            radius=radius, route_width=dummy_gap_feature[4],)
    dummy_path.add_polygon(c.get_region(layer=dummy_layer),layer=dummy_layer) # transfer polygon from c to dummy
    comb = gf.boolean(A=dummy, B= dummy_path, operation='A-B',layer1 = pad_layer, layer2=dummy_layer,layer=pad_layer)
    c.add_ref(comb)
        #clear the dummy layer from the main Component
    c.remove_layers(layers=(dummy_layer,))
    ## ==== start organising optical components ==== ##
    # --- relocation and routing --- #
    gc_in.dxmax, gc_in.dy = bbox_out.dxmax+150, block.dymin-25
    gc_out2.dxmin, gc_out2.dy = bbox_out.dxmin-150, block.dymax+25
    gc_out1.dxmin, gc_out1.dy = bbox_out.dxmin-150, gc_out2.dy+50
    gf.routing.route_single(c,gc_in.ports["o1"],block.ports["o1"],cross_section=xsection)
    gf.routing.route_bundle(c,[gc_out1.ports["o1"],gc_out2.ports["o1"]],[block.ports["o3"],block.ports["o2"]],cross_section=xsection)
    # --- add ports --- #
    for i, pad in enumerate([pad1,pad2]):
        c.add_port(name = f"e{i+1}",port= pad.ports["pad1"],port_type="pad_rf")
    for i, gc in enumerate([gc_in,gc_out1,gc_out2]):
        c.add_port(name = f"vertical_{i+1}", port = gc.ports["vertical_1"])
    c.flatten()
    return c

@gf.cell(check_ports=False)
def MZI_unit(mzi_ref=MZI_racetrack,
             pad_size = (200,100),
             gc_ref=GC_std,
             xsection: CrossSectionSpec = strip_c,
             length_x: int|float = 100,
             length_y: int|float = 10,
             delta_length: int|float = 160,
             radius: int|float = 30,
             **kwargs,
             )->Component:
    # --- load basic components --- #
    c = gf.Component()
    if isinstance(gc_ref,Component):
        gc_in = c.add_ref(gc_ref).mirror_x()
        gc_out1 = c.add_ref(gc_ref)
        gc_out2 = c.add_ref(gc_ref)
    else:
        gc_in = c.add_ref(gc_ref(xsection=xsection,**kwargs)).mirror_x()
        gc_out1 = c.add_ref(gc_ref(xsection=xsection, **kwargs))
        gc_out2 = c.add_ref(gc_ref(xsection=xsection, **kwargs))
    # --- validation --- #
    if length_x<gc_in.dxsize+radius*2+10:
        length_x = gc_in.dxsize+radius*2+10
        gf.logger.warning(f"length x is less than the safety length, automatic correct it to {length_x} um")
    if length_y<127+60-radius*4-delta_length/2:
        length_y = 127+60-radius*4-delta_length/2
        gf.logger.warning(f"length y is less than the safety length, automatic correct it to {length_y} um")
    # --- load MZI block --- #
    block = c.add_ref(mzi_ref(pad_size=pad_size,xsection=xsection, radius=radius, length_x=length_x, length_y=length_y,
                              delta_length=delta_length, **kwargs))
    # --- routing and allocating --- #
    gc_in.dxmin,gc_in.dy = block.ports["o1"].dx+radius*2, block.ports["o1"].dy+127/2
    gf.routing.route_single(c,gc_in.ports["o1"],block.ports["o1"],cross_section=xsection)
    gc_out1.dxmax, gc_out1.dy = block.ports["o3"].dx-radius*2-10, block.ports["o1"].dy-127/2
    gc_out2.dxmax, gc_out2.dy = gc_out1.dxmax, gc_out1.dy-50
    gf.routing.route_bundle(c,[gc_out1.ports["o1"],gc_out2.ports["o1"]],[block.ports["o2"],block.ports["o3"]],cross_section=xsection)
    # --- add ports infomation for the further steps --- #
    for port in block.ports:
        if port.name.startswith("e"):
            c.add_port(name=port.name,port = block.ports[port.name])
    for i, gc in enumerate([gc_in,gc_out1,gc_out2]):
        c.add_port(name = f"vertical_{i+1}", port = gc.ports["vertical_1"])
    c.flatten()
    return c
###################################################################
############           defect detection unit         ##############
###################################################################
@gf.cell(check_ports=False)
def defect_detector(doped_xsection:CrossSection = rib_c_pin,
                    xsection: CrossSectionSpec = rib_c,
                    gc_ref=GC_rib,
                    pad_size: tuple[int|float]=(100,100),
                    pad_pitch: int|float = 150,
                    length: int|float = 1000,
                    pad_layer: LayerSpec = layers["ELC"],
                    pad_gap: int|float = 4,
                    pad_width: int|float = 35,
                    **kwargs,
                    )->Component:
    c = gf.Component()
    wg = c.add_ref(waveguide_with_doping(wg_xsection=doped_xsection,length=length,**kwargs))

    # --- add eletrical components --- #
    record_xmin, record_xmax = 0, 0
    for i in range(2):
        # dynamic change pad length to connect with arm
        pad_size = list(pad_size)
        pad_dimension = pad_size.copy()
        pad_dimension[1] = pad_size[1]+pad_gap+pad_width if i==0 else pad_size[1]
        pad_dimension = tuple(pad_dimension)
        # add pad arm and pads
        arm = c.add_ref(gf.components.rectangle(size=((length+10+pad_size[0]+pad_pitch*(1-i)),pad_width),layer=pad_layer).copy())
        arm.dxmax, arm.dy = wg.dxmax+5, wg.ports["o2"].dy+(pad_gap/2+pad_width/2)*(1-2*i)
        pad_tmplt = c.add_ref(pad(size = pad_dimension,ports="e4",layer=pad_layer).copy())
        pad_tmplt.dxmin, pad_tmplt.dymax = arm.dxmin, arm.dymin
        record_xmin, record_xmax = min(arm.dxmin,record_xmin), max(arm.dxmax, record_xmax)
        # add electric ports #
        c.add_port(name=f"e{i+1}",port = pad_tmplt.ports["e4"],port_type="pad")
    # --- add optical components --- #
    if isinstance(gc_ref,Component):
        gc_in = c.add_ref(gc_ref)
        gc_out = c.add_ref(gc_ref).mirror_x()
    else:
        gc_in = c.add_ref(gc_ref(xsection=xsection,**kwargs))
        gc_out = c.add_ref(gc_ref(xsection=xsection, **kwargs)).mirror_x()
    gc_in.dxmax,gc_in.dy = record_xmin-100, wg.ports["o1"].dy
    gc_out.dxmin, gc_out.dy = record_xmax+100, wg.ports["o2"].dy
    gf.routing.route_single(c,gc_in.ports["o1"],wg.ports["o1"],cross_section=xsection)
    gf.routing.route_single(c,gc_out.ports["o1"],wg.ports["o2"],cross_section=xsection)
    # add optical ports #
    for i, gc in enumerate([gc_in,gc_out]):
        c.add_port(name = f"vertical_{i+1}", port = gc.ports["vertical_1"])
    c.flatten()
    return c

##############################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("utilities")
    c << MZI_unit()
    c.show()
    c.pprint_ports()
