import logging
import os

from pydm.widgets.display_format import DisplayFormat
from qtpy.QtCore import QSize

from ..symbols.gauges import (
    CapManometerGaugeSymbolIcon,
    ColdCathodeComboGaugeSymbolIcon,
    ColdCathodeGaugeSymbolIcon,
    HotCathodeComboGaugeSymbolIcon,
    HotCathodeGaugeSymbolIcon,
    RoughGaugeSymbolIcon,
)
from .base import PCDSSymbolBase
from .mixins import ButtonLabelControl, InterlockMixin, LabelControl, StateMixin

logger = logging.getLogger(__name__)


class RoughGauge(StateMixin, LabelControl, PCDSSymbolBase):
    """
    A Symbol Widget representing a Rough Gauge with the proper icon and
    controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |state      |`On` or `Off`                                                |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        RoughGauge[state="Off"] {
            qproperty-brush: red;
            color: gray;
        }
        RoughGauge[state="On"] {
            qproperty-brush: green;
            color: black;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"

    NAME = "Rough Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GaugePLC"

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            state_suffix=self._state_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = RoughGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(70, 60)

    def get_expert_ui_paths(self, expert_key):
        """
        Provide paths to expert UIs for TurboPump.

        Parameters
        ----------
        expert_key : str
            The expertOphydClass value.

        Returns
        -------
        list[str]
            Paths to matching .ui files, or an empty list.
        """
        if not expert_key:
            return []
        folder = expert_key.rsplit(".", 1)[-1]

        # Expert UIs are stored directly in pump_screens using the pattern:
        # <OphydClass>_<title>.ui (e.g. PIPCombined_detailed.ui).
        ui_dir = os.path.join(os.path.dirname(__file__), "..", "ui", "vacuum", "pump_screens")
        if not os.path.isdir(ui_dir):
            logger.warning(f"No expert UI directory found for {expert_key} at {ui_dir}")
            return []

        prefix = folder + "_"
        all_files = [f for f in os.listdir(ui_dir) if f.startswith(prefix) and f.endswith(".ui")]
        if not all_files:
            logger.warning(f"No expert UI files found for {expert_key} with prefix {prefix} in {ui_dir}")
            return []

        preferred_order = ["detailed.ui", "expert.ui"]

        # Sort by preferred_order, then append any extras not in the list
        ordered_files = [f for f in preferred_order if f in all_files] + [
            f for f in all_files if f not in preferred_order
        ]

        ui_paths = [os.path.join(ui_dir, filename) for filename in ordered_files]
        return ui_paths

    def get_expert_macros(self, expert_key: str, prefix: str) -> dict[str, str]:
        """
        Provide expert-screen macros for IonPump.

        Subclasses can tailor this further for IOC naming differences.
        """
        macros = super().get_expert_macros(expert_key, prefix)

        # Add logic here to add more macros

        return macros


class HotCathodeGauge(ButtonLabelControl, InterlockMixin, StateMixin, PCDSSymbolBase):
    """
    A Symbol Widget representing a Hot Cathode Gauge with the proper icon
    and controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |interlock  |QFrame        |The QFrame wrapping this whole widget. |
    +-----------+--------------+---------------------------------------+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |interlocked|`true` or `false`                                            |
    +-----------+-------------------------------------------------------------+
    |state      |`On`, `Off`, `Starting` or `Error`                           |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        HotCathodeGauge[interlocked="true"] #interlock {
            border: 5px solid red;
        }
        HotCathodeGauge[interlocked="false"] #interlock {
            border: 0px;
        }
        HotCathodeGauge[state="Error"] #icon {
            qproperty-penColor: red;
            qproperty-penWidth: 2;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _interlock_suffix = ":ILK_OK_RBV"
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"
    _command_suffix = ":HV_SW"

    NAME = "Hot Cathode Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GHCPLC"

    SUFFIX_MAP = {}

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            interlock_suffix=self._interlock_suffix,
            state_suffix=self._state_suffix,
            command_suffix=self._command_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = HotCathodeGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(180, 80)


class ColdCathodeGauge(InterlockMixin, StateMixin, ButtonLabelControl, PCDSSymbolBase):
    """
    A Symbol Widget representing a Cold Cathode Gauge with the proper icon and
    controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |interlock  |QFrame        |The QFrame wrapping this whole widget. |
    +-----------+--------------+---------------------------------------+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |interlocked|`true` or `false`                                            |
    +-----------+-------------------------------------------------------------+
    |state      |`On`, `Off`, `Starting` or `Error`                           |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        ColdCathodeGauge[interlocked="true"] #interlock {
            border: 5px solid red;
        }
        ColdCathodeGauge[interlocked="false"] #interlock {
            border: 0px;
        }
        ColdCathodeGauge[state="Error"] #icon {
            qproperty-penColor: red;
            qproperty-penWidth: 2;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _interlock_suffix = ":ILK_OK_RBV"
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"
    _command_suffix = ":HV_SW"

    NAME = "Cold Cathode Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GCCPLC"

    SUFFIX_MAP = {}

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            interlock_suffix=self._interlock_suffix,
            state_suffix=self._state_suffix,
            command_suffix=self._command_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = ColdCathodeGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(180, 80)


class ColdCathodeComboGauge(StateMixin, LabelControl, PCDSSymbolBase):
    """
    A Symbol Widget representing a Combo Cold Cathode and Pirani Gauge with the proper icon and
    controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |state      |`On` or `Off`                                                |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        ColdCathodeComboGauge[state="Off"] {
            qproperty-brush: red;
            color: gray;
        }
        ColdCathodeComboGauge[state="On"] {
            qproperty-brush: green;
            color: black;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"

    NAME = "Cold Combo Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GaugePLC"

    SUFFIX_MAP = {}

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            state_suffix=self._state_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = ColdCathodeComboGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(70, 70)


class HotCathodeComboGauge(StateMixin, LabelControl, PCDSSymbolBase):
    """
    A Symbol Widget representing a Combo Cold Cathode and Pirani Gauge with the proper icon and
    controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |state      |`On` or `Off`                                                |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        HotCathodeComboGauge[state="Off"] {
            qproperty-brush: red;
            color: gray;
        }
        HotCathodeComboGauge[state="On"] {
            qproperty-brush: green;
            color: black;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"

    NAME = "Hot Combo Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GaugePLC"

    SUFFIX_MAP = {}

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            state_suffix=self._state_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = HotCathodeComboGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(70, 70)


class CapacitanceManometerGauge(StateMixin, LabelControl, PCDSSymbolBase):
    """
    A Symbol Widget representing a Rough Gauge with the proper icon and
    controls.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the symbol

    Notes
    -----
    This widget allow for high customization through the Qt Stylesheets
    mechanism.
    As this widget is composed by internal widgets, their names can be used as
    selectors when writing your stylesheet to be used with this widget.
    Properties are also available to offer wider customization possibilities.

    **Internal Components**

    +-----------+--------------+---------------------------------------+
    |Widget Name|Type          |What is it?                            |
    +===========+==============+=======================================+
    |controls   |QFrame        |The QFrame wrapping the controls panel.|
    +-----------+--------------+---------------------------------------+
    |icon       |BaseSymbolIcon|The widget containing the icon drawing.|
    +-----------+--------------+---------------------------------------+
    |pressure   |PyDMLabel     |The pressure reading label.            |
    +-----------+--------------+---------------------------------------+

    **Additional Properties**

    +-----------+-------------------------------------------------------------+
    |Property   |Values                                                       |
    +===========+=============================================================+
    |state      |`On` or `Off`                                                |
    +-----------+-------------------------------------------------------------+

    Examples
    --------

    .. code-block:: css

        CapacitanceMonometerGauge[state="Off"] {
            qproperty-brush: red;
            color: gray;
        }
        CapacitanceMonometerGauge[state="On"] {
            qproperty-brush: green;
            color: black;
        }

    """

    _qt_designer_ = {
        "group": "ECS Vacuum Gauges",
        "is_container": False,
    }
    _state_suffix = ":STATE_RBV"
    _readback_suffix = ":PRESS_RBV"

    NAME = "Capacitance Monometer Gauge"
    EXPERT_OPHYD_CLASS = "pcdsdevices.gauge.GaugePLC"

    SUFFIX_MAP = {}

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            state_suffix=self._state_suffix,
            readback_suffix=self._readback_suffix,
            readback_name="pressure",
            **kwargs,
        )
        self.icon = CapManometerGaugeSymbolIcon(parent=self)
        self.readback_label.displayFormat = DisplayFormat.Exponential

    def sizeHint(self):
        return QSize(70, 70)
