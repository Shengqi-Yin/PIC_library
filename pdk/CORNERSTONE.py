"""
CORNERSTONE PDK — Simplified gdsfactory-compatible Platform Definition
Author: Shengqi Yin
"""

from __future__ import annotations
from typing import Dict, Tuple, Any

from gdsfactory.typings import Layer
from gdsfactory.cross_section import cross_section


# ----------------------------------------------------------------------
# Layer Library
# ----------------------------------------------------------------------

class CornerStoneLayer:
    """Layer library using pure gdsfactory Layer = tuple[int, int]"""

    class General:
        ALG: Layer = (1, 0)
        ALC: Layer = (2, 0)
        OPE: Layer = (22, 0)
        DEF: Layer = (23, 0)
        EDG: Layer = (26, 0)
        FIL: Layer = (39, 0)
        LSH: Layer = (40, 0)
        PAD: Layer = (41, 0)
        ISO: Layer = (46, 0)
        CON: Layer = (47, 0)
        DEE: Layer = (50, 0)
        APO: Layer = (60, 0)
        PRO: Layer = (61, 0)
        TMG: Layer = (62, 0)
        BLE: Layer = (98, 0)
        OUT: Layer = (99, 0)
        LAB: Layer = (100, 0)

    class SOI:
        WGN: Layer = (3, 0)
        WGP: Layer = (4, 0)
        FET: Layer = (5, 0)
        GRA: Layer = (6, 0)
        LPI: Layer = (7, 0)
        LNI: Layer = (8, 0)
        HPI: Layer = (9, 0)
        HNI: Layer = (11, 0)
        VIA: Layer = (12, 0)
        ELC: Layer = (13, 0)
        TRI: Layer = (14, 0)

    class SiN:
        WGN: Layer = (203, 0)
        WGP: Layer = (204, 0)

    class susSi:
        WGP: Layer = (404, 0)

    class GeonSi:
        WGN: Layer = (303, 0)
        WGP: Layer = (304, 0)


# ----------------------------------------------------------------------
# Platform Base Class
# ----------------------------------------------------------------------

class PlatformBase:
    """Base class for unifying layers and cross-sections."""

    platform_layers = None  # override
    widths: Dict[str, float] = None  # override
    radius: Dict[str, float] = 30 # override
    radius_min: Dict[str, float] = 5 # override
    PINs: Dict[str,Any] = None # override
    PNs: Dict[str,Any] = None # override

    def __init__(self,radius: Dict[str, float] = None,
                 radius_min: Dict[str, float] = None,
                 widths: Dict[str, float] = None,
                 PINs: Dict[str, Any] = None,
                 PNs: Dict[str, Any] = None,):
        # --- merge radius ---
        if isinstance(self.radius, dict):
            base_r = self.radius.copy()
            if radius:
                base_r.update(radius)
            self.radius = base_r
        else:
            self.radius = radius or self.radius
        # --- merge radius_min ---
        if isinstance(self.radius_min, dict):
            base_rm = self.radius_min.copy()
            if radius_min:
                base_rm.update(radius_min)
            self.radius_min = base_rm
        else:
            self.radius_min = radius_min or self.radius_min

        # --- merge widths ---
        if isinstance(self.widths, dict):
            base_w = self.widths.copy()
            if widths:
                base_w.update(widths)
            self.widths = base_w
        else:
            self.widths = widths or self.widths

        # --- merge doping --- #
        if isinstance(self.PNs, dict):
            base_PNs = self.PNs.copy()
            if PINs:
                base_PNs.update(PNs)
            self.PNs = base_PNs
        else:
            self.PNs = PNs or self.PNs

        if isinstance(self.PINs, dict):
            base_PINs = self.PINs.copy()
            if PINs:
                base_PINs.update(PINs)
            self.PINs = base_PINs
        else:
            self.PINs = PINs or self.PINs
        # continue original initialization

        self.layers: Dict[str, Layer] = self._merge_layers()
        self._create_cross_sections()

    # ------------------ safe getters -------------------
    def get_radius(self,key:str) -> float:
        """Return platform-specific radius or fallback default"""
        if isinstance(self.radius, dict):
            return self.radius.get(key,PlatformBase.radius)
        return self.radius

    def get_radius_min(self, key: str) -> float:
        """Return platform-specific radius minimum or fallback default"""
        if isinstance(self.radius_min, dict):
            return self.radius_min.get(key, PlatformBase.radius_min)
        return self.radius_min

            # ------------------ LAYER MERGING ------------------

    def _merge_layers(self) -> Dict[str, Layer]:
        """Merge General layers + platform-specific layers into a single dict."""
        merged: Dict[str, Layer] = {}

        # General layers
        for name, value in CornerStoneLayer.General.__dict__.items():
            if isinstance(value, tuple):
                merged[name] = value

        # Platform layers
        for name, value in self.platform_layers.__dict__.items():
            if isinstance(value, tuple):
                merged[name] = value

        return merged

    # ------------------ CROSS SECTIONS ------------------

    def _create_cross_sections(self):
        """Generate cross sections c/o/rib if available."""
        WGN = self.layers.get("WGN")
        WGP = self.layers.get("WGP")
        FET = self.layers.get("FET")  # optional layer
        HPI, HNI = self.layers.get("HPI"), self.layers.get("HNI")
        LPI, LNI = self.layers.get("LPI"), self.layers.get("LNI")

        # --- strip c ---
        if "c" in self.widths:
            self.c = cross_section(
                width=self.widths["c"],
                layer=WGN,
                radius=self.get_radius("c"),
                radius_min=self.get_radius_min("c"),
                sections=[],
            )

        # --- strip o ---
        if "o" in self.widths:
            self.o = cross_section(
                width=self.widths["o"],
                layer=WGN,
                radius=self.get_radius("o"),
                radius_min=self.get_radius_min("o"),
                sections=[],
            )

        # --- strip visible ---
        if "vis520" in self.widths:
            self.vis520 = cross_section(
                width = self.widths["vis520"],
                layer=WGN,
                radius=self.get_radius("vis520"),
                radius_min=self.get_radius_min("vis520"),
                sections=[],
            )
        if "vis638" in self.widths:
            self.vis638 = cross_section(
                width = self.widths["vis638"],
                layer=WGN,
                radius=self.get_radius("vis638"),
                radius_min=self.get_radius_min("vis638"),
                sections=[],
            )
        if "vis780" in self.widths:
            self.vis780 = cross_section(
                width = self.widths["vis780"],
                layer=WGN,
                radius=self.get_radius("vis780"),
                radius_min=self.get_radius_min("vis780"),
                sections=[],
            )

        # --- rib cross-sections (if RIB layer exists) ---
        if FET:
            if "c" in self.widths:
                self.rib_c = cross_section(
                    width=self.widths["c"],
                    layer=WGN,
                    radius=self.get_radius("c"),
                    radius_min=self.get_radius_min("c"),
                    sections=[{"layer": FET,"width":self.widths["c"]+10}],
                )
            if "o" in self.widths:
                self.rib_o = cross_section(
                    width=self.widths["o"],
                    layer=WGN,
                    radius=self.get_radius("o"),
                    radius_min=self.get_radius_min("o"),
                    sections=[{"layer": FET,"width":self.widths["c"]+10}],
                )
            # --- dope cross-sections (if dope layer exists)
            if HPI and HNI:
                if "c" in self.widths:
                    width_h = self.PINs["c"].get("width_h")
                    gap_h = self.PINs["c"].get("gap_h")
                    doped_offset = width_h/2+gap_h+self.widths["c"]/2
                    self.rib_c_pin = xsection_add_sections(self.rib_c,{"layer":HPI, "width":width_h,"offset":doped_offset},
                                                           {"layer":HNI, "width":width_h,"offset":-doped_offset})
                if "o" in self.widths:
                    width_h = self.PINs["o"].get("width_h")
                    gap_h = self.PINs["o"].get("gap_h")
                    doped_offset = width_h/2+gap_h+self.widths["o"]/2
                    self.rib_o_pin = xsection_add_sections(self.rib_o,{"layer":HPI, "width":width_h,"offset":doped_offset},
                                                           {"layer":HNI, "width":width_h,"offset":-doped_offset})
                if LPI and LNI:
                    if "c" in self.widths:
                        band = "c"
                        width_hp, width_hn, width_lp, width_ln = self.PNs[band].get("width_hp"), self.PNs[band].get(
                            "width_hn"),self.PNs[band].get("width_lp"),self.PNs[band].get("width_ln")
                        gap_hp, gap_hn, offset_lp, offset_ln = self.PNs[band].get("gap_hp"), self.PNs[band].get(
                            "gap_hn"), self.PNs[band].get("offset_lp"), self.PNs[band].get("offset_ln")
                        offset_hp, offset_hn = width_hp/2+gap_hp+self.widths[band]/2, width_hn/2+gap_hn+self.widths[band]/2
                        self.rib_c_pn = xsection_add_sections(self.rib_c,{"layer":HPI, "width":width_hp,"offset":-offset_hp},
                                                               {"layer":HNI, "width":width_hn,"offset":offset_hn},
                                                               {"layer":LPI, "width":width_lp,"offset":offset_lp},
                                                               {"layer":LNI, "width":width_ln,"offset":offset_ln})
                    if "o" in self.widths:
                        band = "o"
                        width_hp, width_hn, width_lp, width_ln = self.PNs[band].get("width_hp"), self.PNs[band].get(
                            "width_hn"),self.PNs[band].get("width_lp"),self.PNs[band].get("width_ln")
                        gap_hp, gap_hn, offset_lp, offset_ln = self.PNs[band].get("gap_hp"), self.PNs[band].get(
                            "gap_hn"), self.PNs[band].get("offset_lp"), self.PNs[band].get("offset_ln")
                        offset_hp, offset_hn = width_hp/2+gap_hp+self.widths[band]/2, width_hn/2+gap_hn+self.widths[band]/2
                        self.rib_o_pn = xsection_add_sections(self.rib_o,{"layer":HPI, "width":width_hp,"offset":-offset_hp},
                                                               {"layer":HNI, "width":width_hn,"offset":offset_hn},
                                                               {"layer":LPI, "width":width_lp,"offset":offset_lp},
                                                               {"layer":LNI, "width":width_ln,"offset":offset_ln})

##### function tools ########
def xsection_add_sections(xs,*new_sections: dict):
    """return a new cross section with an extra section appended"""
    xsection_new = cross_section(width=xs.width, layer=xs.layer, radius=xs.radius, radius_min=xs.radius_min,
                                 sections=list(xs.sections[1:])+list(new_sections))
    return xsection_new
# ----------------------------------------------------------------------
# Platform Implementations
# ----------------------------------------------------------------------

class SOI(PlatformBase):
    platform_layers = CornerStoneLayer.SOI
    radius = {"c": 30, "o": 30}
    radius_min = {"c": 10, "o":10}
    widths = {"c": 0.45, "o": 0.40}
    # doping for active, rib only
    PINs = {"c":{"gap_h":0.05,"width_h":35},
             "o":{"gap_h":0.05,"width_h":35},}
    PNs = {"c":{"gap_hp":0.575,"gap_hn":0.525,"offset_lp":-5,"offset_ln":2.5,
                "width_hp":10, "width_hn":12,"width_lp":23,"width_ln":5,},
           "o":{"gap_hp":0.5,"gap_hn":0.55,"offset_lp":-5,"offset_ln":2.5,
                "width_hp":10, "width_hn":12,"width_lp":23,"width_ln":5,},}

class SiN(PlatformBase):
    platform_layers = CornerStoneLayer.SiN
    radius = {"c": 80, "o": 80,
              "vis520":50, "vis638":50, "vis780":50}
    radius_min = {"c": 30, "o": 30,
                  "vis520":15, "vis638":15, "vis780":15}
    widths = {"c": 1.20, "o": 0.95,
              "vis520":0.27, "vis638":0.36, "vis780":0.50}


# ----------------------------------------------------------------------
# Platform Factory
# ----------------------------------------------------------------------

def PLATFORM(name: str, **kwargs) -> PlatformBase:
    """
    Future supplementary command: e.g.
    PLATFORM("SiN", radius={"vis520": 50}, radius_min={"vis638": 20})
    """
    name = name.lower()
    if name == "soi":
        return SOI( **kwargs)
    if name == "sin":
        return SiN( **kwargs)
    raise ValueError(f"Unknown platform {name}")


# ----------------------------------------------------------------------
# Test Run
# ----------------------------------------------------------------------

if __name__ == "__main__":
    p = PLATFORM("SOI")
    # print("Merged Layers:", p.layers["ALG"])
    print("Cross-section c:", p.rib_c_pn)
    # print("Cross-section o:", p.o)

    import gdsfactory as gf
    c = gf.Component()
    p1 = gf.path.straight(length=10)
    c = p1.extrude(p.rib_o_pn)
    c.show()
