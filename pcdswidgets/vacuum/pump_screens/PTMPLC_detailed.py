"""
Originally generated from jinja template ui_main_widget.j2

This file can be safely edited to change the runtime behavior of the widget.
"""

from pcdswidgets.builder.designer_options import DesignerOptions
from pcdswidgets.builder.icon_options import IconOptions
from pcdswidgets.generated.vacuum.pump_screens.PTMPLC_detailed_base import PtmplcDetailedBase


class PtmplcDetailed(PtmplcDetailedBase):
    designer_options = DesignerOptions(
        group="ECS Vacuum Pump_Screens",
        is_container=False,
        icon=IconOptions.NONE,
    )
