"""
SkyGuard AI - Physics-Informed Atmospheric Thermodynamics Module
Author: SkyGuard AI Development Team
Focus: Core Triad - Temperature (°C), Atmospheric Pressure (hPa), Relative Humidity (%)
"""

import math
from typing import Dict, Any, Tuple, Optional


class AtmosphericThermodynamics:
    """
    Thermodynamic and psychrometric relations for boundary layer meteorology.
    Implements standard WMO/NOAA physical equations for atmospheric quality control.
    """

    # Physical Constants
    R_DRY = 287.058     # Specific gas constant for dry air (J/(kg·K))
    R_VAPOR = 461.495   # Specific gas constant for water vapor (J/(kg·K))
    C_P = 1005.0        # Specific heat capacity of dry air at constant pressure (J/(kg·K))
    EPSILON = 0.622     # Ratio of molecular weights (M_v / M_d)
    P_STANDARD = 1013.25 # Standard sea-level atmospheric pressure (hPa)
    T_ZERO_C = 273.15   # 0°C in Kelvin

    # Magnus-Tetens Parameters (WMO Recommended coefficients for -45°C <= T <= 50°C)
    MAGNUS_A = 17.625
    MAGNUS_B = 243.04   # °C

    @classmethod
    def saturation_vapor_pressure(cls, temp_c: float) -> float:
        """
        Calculate Saturation Vapor Pressure e_s(T) in hPa (millibars) using Magnus-Tetens formula.
        Valid for -45°C <= T <= 50°C.
        """
        e_s = 6.1094 * math.exp((cls.MAGNUS_A * temp_c) / (cls.MAGNUS_B + temp_c))
        return round(e_s, 3)

    @classmethod
    def actual_vapor_pressure(cls, temp_c: float, humidity_pct: float) -> float:
        """
        Calculate Actual Vapor Pressure e(T, RH) in hPa.
        e = (RH / 100) * e_s(T)
        """
        rh_clamped = max(0.001, min(100.0, humidity_pct))
        e_s = cls.saturation_vapor_pressure(temp_c)
        e = (rh_clamped / 100.0) * e_s
        return round(e, 3)

    @classmethod
    def dew_point(cls, temp_c: float, humidity_pct: float) -> float:
        """
        Calculate theoretical Dew Point Temperature T_d in °C.
        Derived from inverted Magnus-Tetens relationship.
        """
        rh_clamped = max(0.01, min(100.0, humidity_pct))
        alpha = ((cls.MAGNUS_A * temp_c) / (cls.MAGNUS_B + temp_c)) + math.log(rh_clamped / 100.0)
        t_d = (cls.MAGNUS_B * alpha) / (cls.MAGNUS_A - alpha)
        return round(t_d, 2)

    @classmethod
    def dew_point_depression(cls, temp_c: float, humidity_pct: float) -> float:
        """
        Calculate Dew Point Depression (T - T_d) in °C.
        Physical invariant: (T - T_d) MUST be >= 0 in non-supersaturated atmospheric air.
        """
        t_d = cls.dew_point(temp_c, humidity_pct)
        return round(temp_c - t_d, 2)

    @classmethod
    def virtual_temperature(cls, temp_c: float, pressure_hpa: float, humidity_pct: float) -> float:
        """
        Calculate Virtual Temperature T_v in Kelvin and °C.
        T_v = T_K * (1 + 0.378 * (e / P))
        Accounts for lower density of moist air relative to dry air.
        """
        t_k = temp_c + cls.T_ZERO_C
        e = cls.actual_vapor_pressure(temp_c, humidity_pct)
        p_safe = max(500.0, pressure_hpa)
        t_v_k = t_k * (1.0 + 0.378 * (e / p_safe))
        return round(t_v_k - cls.T_ZERO_C, 2)

    @classmethod
    def moist_air_density(cls, temp_c: float, pressure_hpa: float, humidity_pct: float) -> float:
        """
        Calculate Moist Air Density rho in kg/m^3.
        rho = (P_dry / (R_d * T)) + (e / (R_v * T))
        """
        t_k = temp_c + cls.T_ZERO_C
        p_pa = pressure_hpa * 100.0  # convert hPa to Pa
        e = cls.actual_vapor_pressure(temp_c, humidity_pct)
        e_pa = e * 100.0
        p_dry_pa = max(0.0, p_pa - e_pa)

        rho = (p_dry_pa / (cls.R_DRY * t_k)) + (e_pa / (cls.R_VAPOR * t_k))
        return round(rho, 4)

    @classmethod
    def potential_temperature(cls, temp_c: float, pressure_hpa: float) -> float:
        """
        Calculate Potential Temperature theta in °C (referred to 1000 hPa).
        theta = T_K * (1000 / P)^(R_d / C_p) - 273.15
        Conserved under dry adiabatic processes.
        """
        t_k = temp_c + cls.T_ZERO_C
        p_safe = max(300.0, pressure_hpa)
        kappa = cls.R_DRY / cls.C_P  # ~0.286
        theta_k = t_k * math.pow(1000.0 / p_safe, kappa)
        return round(theta_k - cls.T_ZERO_C, 2)

    @classmethod
    def validate_thermodynamic_consistency(
        cls,
        temp_c: float,
        pressure_hpa: float,
        humidity_pct: float,
        reported_dew_point: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute comprehensive thermodynamic consistency checks across T, P, RH.
        Returns detailed validation diagnostics and thermodynamic indicators.
        """
        violations = []
        is_consistent = True

        # 1. Physical range bounds
        if not (-60.0 <= temp_c <= 60.0):
            violations.append(f"Temperature {temp_c}°C outside terrestrial atmospheric bounds [-60, +60°C]")
            is_consistent = False

        if not (0.0 <= humidity_pct <= 100.0):
            violations.append(f"Relative humidity {humidity_pct}% outside physical bounds [0, 100%]")
            is_consistent = False

        if not (500.0 <= pressure_hpa <= 1090.0):
            violations.append(f"Atmospheric pressure {pressure_hpa} hPa outside surface atmospheric bounds [500, 1090 hPa]")
            is_consistent = False

        # 2. Derived thermodynamic quantities
        e_s = cls.saturation_vapor_pressure(temp_c)
        e = cls.actual_vapor_pressure(temp_c, humidity_pct)
        calc_td = cls.dew_point(temp_c, humidity_pct)
        depr = temp_c - calc_td
        rho = cls.moist_air_density(temp_c, pressure_hpa, humidity_pct)
        theta = cls.potential_temperature(temp_c, pressure_hpa)
        t_v = cls.virtual_temperature(temp_c, pressure_hpa, humidity_pct)

        # 3. Super-saturation & Dew Point Inversion check
        effective_td = reported_dew_point if reported_dew_point is not None else calc_td
        if effective_td > temp_c + 0.2:
            violations.append(
                f"Thermodynamic Violation: Dew point ({effective_td:.2f}°C) exceeds ambient temperature ({temp_c:.2f}°C). "
                f"Relative humidity sensor positive calibration bias or thermal probe lag."
            )
            is_consistent = False

        # 4. Vapor pressure consistency
        if e > e_s * 1.02:
            violations.append(
                f"Vapor pressure inconsistency: Actual vapor pressure ({e:.2f} hPa) exceeds saturation ({e_s:.2f} hPa)."
            )
            is_consistent = False

        # 5. Reported Dew Point vs Theoretical Magnus deviation
        if reported_dew_point is not None and abs(reported_dew_point - calc_td) > 3.0:
            violations.append(
                f"Reported dew point ({reported_dew_point:.2f}°C) diverges from Magnus formula ({calc_td:.2f}°C) by {abs(reported_dew_point - calc_td):.2f}°C."
            )
            is_consistent = False

        return {
            "is_consistent": is_consistent,
            "violations": violations,
            "metrics": {
                "saturation_vapor_pressure_hpa": e_s,
                "actual_vapor_pressure_hpa": e,
                "calculated_dew_point_c": calc_td,
                "dew_point_depression_c": depr,
                "air_density_kg_m3": rho,
                "potential_temperature_c": theta,
                "virtual_temperature_c": t_v
            }
        }
