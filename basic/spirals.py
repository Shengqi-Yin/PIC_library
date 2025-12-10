from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from functions.path_spiral import spiral_archimedean
from pdk.CORNERSTONE import PLATFORM
from basic.tapers import taper_sm2sm
###################################################
strip_c = PLATFORM("SOI").c #load a cross section for strip waveguide


@gf.cell
def spiral_double_oppositeIOs(
        min_bend_radius: float = 10.0,
        separation: float = 2.0,
        number_of_loops: float = 3,
        npoints: int = 1001,
        width: float = 1.2,
        layer: LayerSpec = (10, 0),
        bend: ComponentSpec = "bend_circular",
) -> gf.Component:
    component = gf.Component()
    ### Generate central s-bend region
    s = gf.Section(width=width, offset=0, layer=layer, port_names=("o1", "o2"))
    x = gf.CrossSection(sections=(s,))
    xs = gf.cross_section.cross_section(width=width, offset=0, port_names=("o1", "o2"), layer=layer)

    bend = gf.get_component(bend, radius=min_bend_radius / 2, angle=180, cross_section=x)
    bend1 = component.add_ref(bend).rotate(90)
    bend2 = component.add_ref(bend)
    bend2.connect("o2", bend1.ports["o1"], mirror=True)
    ### Generate main spiral region
    path = spiral_archimedean(
        min_bend_radius=min_bend_radius,
        separation=separation,
        number_of_loops=number_of_loops,
        npoints=npoints,
    )
    path.start_angle = 90
    path.end_angle = 90

    spiral = path.extrude(xs)
    spiral1 = component.add_ref(spiral)
    spiral2 = component.add_ref(spiral)
    spiral2.dmirror()

    spiral1.connect("o1", bend2.ports["o1"])
    spiral2.connect("o1", bend1.ports["o2"], mirror=True)

    ### Generate input and output terminals
    x = (separation * number_of_loops * 2 + min_bend_radius) * np.cos(number_of_loops * 2 * np.pi)
    y = (separation * number_of_loops * 2 + min_bend_radius) * np.sin(number_of_loops * 2 * np.pi)

    path_in = spiral_archimedean(min_bend_radius=np.sqrt(x ** 2 + y ** 2), separation=separation, number_of_loops=0.5,
                                 npoints=npoints * 2)
    path_out = spiral_archimedean(min_bend_radius=np.sqrt(x ** 2 + y ** 2), separation=separation, number_of_loops=0.25,
                                  npoints=npoints * 2)
    path_in.start_angle = 90
    path_in.end_angle = -90
    path_out.start_angle = 90
    path_out.end_angle = 180
    spiral_out = path_out.extrude(xs)
    spiral_in = path_in.extrude(xs)
    spiral_input = component.add_ref(spiral_in)
    spiral_output1 = component.add_ref(spiral_out)
    spiral_output1.dmirror()
    spiral_output2 = component.add_ref(spiral_out)
    spiral_output2.dmirror()
    spiral_input.connect("o1", spiral1.ports["o2"])
    spiral_output1.connect("o1", spiral2.ports["o2"], mirror=True)
    spiral_output2.connect("o1", spiral_input.ports["o2"])
    component.add_port("o1", port=spiral_output2.ports["o2"])
    component.add_port("o2", port=spiral_output1.ports["o2"])
    component.info["length"] = float(path.length() + bend.info["length"]) * 2 + path_in.length() + path_out.length() * 2
    component.flatten()
    # print(component.info)
    return component


def spiral_double_racetrack_oppositeIOs(
        min_bend_radius: float = 55.0,
        separation: float = 5,
        number_of_loops: float = 3,
        npoints: int = 1001,
        width: float = 1.2,
        wg_length: int | float = 10,
        hyperbola: float = 1,
        taper_width: float = 2,
        taper_length: float = 50,
        layer: LayerSpec = (10, 0),
        xsection: CrossSectionSpec = None,
        bend: ComponentSpec = "bend_circular",
        labels: list|str|None = None,
        label_size: int|float = 10,
) -> gf.Component:
    # --- validation --- #
    if xsection:
        layer = xsection.layer
        width= xsection.width
    if taper_width == width:
        taper_length = 0
    # --- layout --- #
    c = gf.Component()
    xs = gf.cross_section.cross_section(width=width, layer=layer, port_names=("o1", "o2"))
    bend = spiral_archimedean(min_bend_radius=min_bend_radius,
                              separation=0, number_of_loops=0.5,
                              npoints=npoints)
    bend.start_angle = 90
    bend.end_angle = 270
    bend1 = c.add_ref(bend.extrude(xs)).rotate(90)
    bend2 = c.add_ref(bend.extrude(xs))
    straight = c.add_ref(
        taper_sm2sm(width_sm=width, width_mm=taper_width, mmi_length=wg_length, taper_length=taper_length,
                       layer=layer, m=hyperbola))
    c.info["length"] = float(wg_length + 2 * taper_length)
    straight.connect("o1", bend1.ports["o1"])
    bend2.connect("o2", straight.ports["o2"], mirror=True)
    path = spiral_archimedean(min_bend_radius=min_bend_radius,
                              separation=0, number_of_loops=0.25,
                              npoints=npoints)
    path.start_angle = 90
    path.end_angle = 180
    spiral = path.extrude(xs)
    spiral_length = path.length()
    for num in range(number_of_loops * 2):
        ttt_1 = taper_sm2sm(width_sm=width, width_mm=taper_width, taper_length=taper_length, layer=layer,
                               m=hyperbola,
                               mmi_length=wg_length + separation * 2 * (num + 0.5))
        ttt_2 = taper_sm2sm(width_sm=width, width_mm=taper_width, taper_length=taper_length, layer=layer,
                               m=hyperbola,
                               mmi_length=min_bend_radius * 2 - taper_length * 2 + separation * 2 * (num + 0.5))

        if num == 0:
            straight1a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 0.5) + 2 * taper_length)
            straight1a.connect("o1", bend1.ports["o2"])
            spiral1a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral1a.connect("o1", straight1a.ports["o2"])
            straight2a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 0.5) + 2 * taper_length)
            straight2a.connect("o1", bend2.ports["o1"])
            spiral2a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral2a.connect("o1", straight2a.ports["o2"])

        else:
            straight1a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 0.5) + 2 * taper_length)
            straight1a.connect("o1", spiral1a.ports["o2"])
            spiral1a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral1a.connect("o1", straight1a.ports["o2"])
            straight2a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 0.5) + 2 * taper_length)
            straight2a.connect("o1", spiral2a.ports["o2"])
            spiral2a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral2a.connect("o1", straight2a.ports["o2"])
        straight1b = c.add_ref(ttt_2)
        c.info["length"] += float(
            min_bend_radius * 2 - taper_length * 2 + separation * 2 * (num + 0.5) + 2 * taper_length)
        straight1b.connect("o1", spiral1a.ports["o2"])
        spiral1a = c.add_ref(spiral)
        c.info["length"] += float(spiral_length)
        spiral1a.connect("o1", straight1b.ports["o2"])
        straight2b = c.add_ref(ttt_2)
        c.info["length"] += float(
            min_bend_radius * 2 - taper_length * 2 + separation * 2 * (num + 0.5) + 2 * taper_length)
        straight2b.connect("o1", spiral2a.ports["o2"])
        spiral2a = c.add_ref(spiral)
        c.info["length"] += float(spiral_length)
        spiral2a.connect("o1", straight2b.ports["o2"])

        if num == number_of_loops * 2 - 1:
            ttt_1 = taper_sm2sm(width_sm=width, width_mm=taper_width, taper_length=taper_length, layer=layer,
                                   m=hyperbola,
                                   mmi_length=wg_length + separation * 2 * (num + 1.5))
            ttt_2 = taper_sm2sm(width_sm=width, width_mm=taper_width, taper_length=taper_length, layer=layer,
                                   m=hyperbola,
                                   mmi_length=min_bend_radius * 2 - taper_length * 2 + separation * 2 * (num + 1))
            straight1a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 1.5) + 2 * taper_length)
            straight1a.connect("o1", spiral1a.ports["o2"])
            straight2a = c.add_ref(ttt_1)
            c.info["length"] += float(wg_length + separation * 2 * (num + 1.5) + 2 * taper_length)
            straight2a.connect("o1", spiral2a.ports["o2"])
            spiral2a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral2a.connect("o1", straight2a.ports["o2"])
            straight2b = c.add_ref(ttt_2)
            c.info["length"] += float(
                min_bend_radius * 2 - taper_length * 2 + separation * 2 * (num + 1) + 2 * taper_length)
            straight2b.connect("o1", spiral2a.ports["o2"])
            spiral2a = c.add_ref(spiral)
            c.info["length"] += float(spiral_length)
            spiral2a.connect("o2", straight2b.ports["o2"])

    c.add_port(name="o1", port=spiral2a.ports["o1"], layer=layer)
    c.add_port(name="o2", port=straight1a.ports["o2"], layer=layer)
    if labels:
        for i, label in enumerate(labels):
            if label == "length":
                txt = c.add_ref(gf.c.text(text=f"length = {round(c.info["length"]/1000,1)} mm", layer=xsection.layer, size=label_size))
            else:
                txt = c.add_ref(gf.c.text(text=f"{label}", layer=xsection.layer, size=label_size))
            txt.dxmax, txt.dymin = spiral2a.dxmin-10, straight1a.dymax + 10 + (label_size + 3) * i
    print(f"path length = {c.info["length"]} um")
    # c.draw_ports()
    # c.flatten()
    return c



###################################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("spirals")
    c <<spiral_double_racetrack_oppositeIOs(layer=strip_c.layer,labels=["length"])
    c.show()
