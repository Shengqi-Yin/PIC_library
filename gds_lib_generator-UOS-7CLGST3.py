from pdk.components_in_platform import SOI220_lib,SiN300_lib, SiN200_lib, SOI500_lib, SOI340_lib, SOI220active_lib
from functions.env import *
import klayout.db as pya
import yaml
import stat
import shutil
from pathlib import Path
# import warnings
# warnings.filterwarnings("ignore", category=EOFError)
######################################################################
### Packaging function tool 1:
### extracted all components and port info from the pre-built cell library
### shallow delete the top cell to release all component in 1st level
### save the flatten and plained component list as a lib-template
#####################################################################
def packaging_as_library(
        dir_path:str|None = None,
        cell_lib: list|dict|None = None,
        save_folder_name: str = "cell_library",
        save_gds_name: str = "cell_library",
        flatten: bool = False,
    ):
    """
    This function can package the cell_library to the gds template be used for pdk website
    :param dir_path: target folder direction
    :param cell_lib: cell library
    :param save_gds_name: output gds file name
    :param flatten: flattern all subcell in the gds template
    """
    # --- resolve dir_path --- #
    # if dir_path is None or not os.path.exists(dir_path):
    #     print(f"dir_path: {dir_path} is invalid, use current working directory: {os.getcwd()}.")
    #     dir_path = os.getcwd()
    # dir_path = Path(dir_path)
    # --- Create or cover the save_gds_name --- #
    if dir_path is None:
        output_gds = save_folder_name/f"{save_gds_name}.gds"
    output_gds = dir_path/f"{save_gds_name}.gds"
    # --- load cell unit from libray --- #

    c = gf.Component()
    for name,cell in cell_lib.items():
        if flatten:
            cell.name = name
            cell.flatten()
        c.add_ref(cell)
        c.add_ports(cell.ports)
    c.write_gds(output_gds,with_metadata=True)
    # --- shallow delete the top cell to flat the lib --- #
    layout = pya.Layout()
    layout.read(output_gds)
    top_cell = layout.top_cells()[0]
    top_cell.delete()
    layout.write(output_gds)

##################################################
### Packaging function tool 2:
##################################################
# -- extract information from the component name --- #
def _parse_wavelength(name:str):
    parts = name.lower().split("_")
    # wavelength band
    if any(p=="cband" for p in parts):
        return 1550
    if any(p == "oband" for p in parts):
        return 1310
    # wavelength with unit
    for p in parts:
        if p.endswith("nm"):
            num = p.replace("nm","")
            if num.isdigit():
                return int(num)
    # wavelength in digit only
    for p in parts:
        if p.isdigit():
            return int(p)
    return None

def _parse_polarisation(name:str):
    if "te" in name.lower():
        pol = "TE"
    elif "tm" in name.lower():
        pol = "TM"
    else:
        pol = "None"
    return pol

def _parse_cross_section(name:str):
    if "strip" in name.lower():
        return "strip"
    elif "rib" in name.lower():
        return "rib"
    return "strip"

def _parse_from_name(name:str):
    return _parse_wavelength(name),_parse_polarisation(name),_parse_cross_section(name)

# --- extract information from component info and specification --- #
def _extract_comp_type(comp:ComponentSpec):
    if "component_type" in comp.info:
        return comp.info["component_type"]
    return None

def _extract_fiber_type(comp: ComponentSpec):
    comp_type = comp.info.get("component_type", "")
    if comp_type in ("GratingCoupler1D", "GratingCoupler2D", "EdgeCoupler","PackagingTemplate"):
        fiber_type = comp.info.get("fiber_type","")
        if fiber_type:
            fiber_type = fiber_type
        else:
            fiber_type = "SMF28"
        coupling_angle = comp.info.get("coupling_angle_cladding","")
        if coupling_angle:
            coupling_angle = coupling_angle
        else:
            coupling_angle = 6.9
        return fiber_type,coupling_angle
    return None,None

def _normalize_port_type(port_type:str, pol:str):
    if "vertical" in port_type:
        return f"vertical_{pol.lower()}"
    elif port_type in ("pad","electrical"):
        return f"electrical_dc"
    else:
        return port_type

# --- Convert Component name and information to YAML dictionary --- #
def component_to_yaml_dict(str_name:str, component:ComponentSpec):
    wavelength,polarisation,xs_section = _parse_from_name(str_name)
    component_type = _extract_comp_type(component)
    fiber_type, coupling_angle = _extract_fiber_type(component)
    ports_yaml =[]
    if component.ports:
        for port in component.ports:
            port_type = port.port_type if hasattr(port,"port_type") else "optical"
            # --- for vertical port need force update port name --- #
            port_type = _normalize_port_type(port_type, polarisation)
            port_info = {
                "name": port.name,
                "port_type": port_type,
                "center":[round(port.center[0],3),round(port.center[1],3)],
                "orientation":round(port.orientation,1),
            }
            # add crossection for optical and electrical port
            if "optical" in port_type:
                port_info["cross_section"] = f"{xs_section}_{wavelength}nm_{polarisation}"
            elif "electrical_dc" in port_type or "pad_dc" in port_type:
                port_info["cross_section"] = "dc"
            # for the port with width
            pt = port.port_type.lower()
            if pt.startswith("vertical") or pt.startswith("edge"):
                need_width = 1
            else:
                need_width = 0
            if hasattr(port,"width") and need_width:
                port_info["width"] = round(port.width,3)
            # TE/TM modes in optical port
            if polarisation and port_type=="optical":
                port_info["modes"]=[{
                    "mode_numbers":[0,0],
                    "polarisations":polarisation,
                    "wavelength":wavelength,
                }]
            ports_yaml.append(port_info)
            if port_type in ("vertical_te","vertical_tm","edge"):
                port_info["coupling_angle_cladding"] = coupling_angle
                port_info["fibre_modes"] = [
                    {"fibre_type":fiber_type,
                     "wavelength":wavelength,
                     }
                ]
    if component_type is None and component.ports is None:
        return {"name": str_name}
    else:
        return {"name": str_name,"ports":ports_yaml}

    return {"name":str_name,
            "component_type":component_type,
            "ports":ports_yaml}

def write_component_yaml(str_name:str,
                         component:ComponentSpec,
                         output_yaml=None):
    data = component_to_yaml_dict(str_name, component)
    yaml_name = output_yaml if output_yaml else str_name+".yaml"
    with open(yaml_name, "w") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    print(f"YAML written to {yaml_name}")


def packaging_as_pdk(
        dir_path:str|None = None,
        cell_lib: list|dict|None = None,
        save_folder_name: str = "cell_library",
        flatten: bool = True,
    ):
    """
    Pack components into a PDK folder and generate YAMLs.
    - dir_path: root path to save; if None or invalid, use current working directory.
    - cell_lib: dict {"name": component} or list of (name, component).
    - save_folder_name: target folder under dir_path.
    - flatten: reserved, currently used.
    """

    # --- solving cell lib --- #
    if cell_lib is None:
        print("invalid library name, terminated")
        return
    for name,comp in cell_lib.items():
        print(f"Start solving {name}")
        output_yaml = dir_path / f"{name}.yaml"
        output_gds = dir_path / f"{name}.gds"
        write_component_yaml(name,comp,output_yaml)
        print(f"Finish solving {name}")
        comp.name = name
        comp.flatten()
        c = comp
        c.write_gds(output_gds, with_metadata=True)

    print("\n all Components have been packaged")

def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def packaging_lib_and_comps(dir_path:str|None = None,
        cell_lib: list|dict|None = None,
        save_folder_name: str = "cell_library_test",
        save_lib_name: str = None,
        flatten: bool = True):
    # --- resolve dir_path --- #
    if dir_path is None or not os.path.exists(dir_path):
        print(f"dir_path: {dir_path} is invalid, use current working directory: {os.getcwd()}.")
        dir_path = os.getcwd()
    dir_path = Path(dir_path)
    # --- Create or empty the save_folder_name --- #
    target_folder = dir_path / save_folder_name
    if target_folder.exists():
        print(f"target folder already exists: {target_folder}, please manually remove it")
        answer = input("Have you remove the folder? (y/n): ").strip().lower()
        if answer == "y":
            if target_folder.exists():
                print("You are lying (WE DO NOT WELCOME LIER!).")
                return
            print("continue to packaging")
        if answer == "overwrite":
            shutil.rmtree(target_folder, onerror=remove_readonly)
            print("On you command to empty the folder")
        else:
            print("user give up")
            return
    target_folder.mkdir(parents=True, exist_ok=True)
    print(f"target_folder: {target_folder} created")

    packaging_as_pdk(dir_path=target_folder,cell_lib=cell_lib,save_folder_name=save_folder_name,
                     flatten=flatten)
    packaging_as_library(dir_path=target_folder, cell_lib=cell_lib, save_folder_name=save_folder_name,
                         save_gds_name=save_lib_name, flatten=flatten)

##### ==== main panel ==== ##
if __name__ == "__main__":
    # packaging_lib_and_comps(cell_lib=SOI220_lib, save_lib_name="SOI220_library_template",save_folder_name="SOI220_CELLS")
    packaging_lib_and_comps(cell_lib=SOI220active_lib, save_lib_name="SOI220active_library_template",save_folder_name="SOI220active_CELLS")
    # packaging_lib_and_comps(cell_lib=SOI340_lib, save_lib_name="SOI340_library_template",save_folder_name="SOI340_CELLS")
    # packaging_lib_and_comps(cell_lib=SOI500_lib, save_lib_name="SOI500_library_template",save_folder_name="SOI500_CELLS")
    # packaging_lib_and_comps(cell_lib=SiN300_lib, save_lib_name="SiN300_library_template",save_folder_name="SiN300_CELLS")
    # packaging_lib_and_comps(cell_lib=SiN200_lib, save_lib_name="SiN200_library_template",save_folder_name="SiN200_CELLS")