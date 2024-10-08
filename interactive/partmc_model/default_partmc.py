import numpy as np
import PyPartMC as ppmc
from PyPartMC import si

# This file is based on https://github.com/open-atmos/PyPartMC/blob/main/examples/process_simulation_output.ipynb
# It is the default pypartmc configuration


def run_pypartmc_model(session_id):
    gas_data = ppmc.GasData(
        ("H2SO4",
         "HNO3",
         "HCl",
         "NH3",
         "NO",
         "NO2",
         "NO3",
         "N2O5",
         "HONO",
         "HNO4",
         "O3",
         "O1D",
         "O3P",
         "OH",
         "HO2",
         "H2O2",
         "CO",
         "SO2",
         "CH4",
         "C2H6",
         "CH3O2",
         "ETHP",
         "HCHO",
         "CH3OH",
         "ANOL",
         "CH3OOH",
         "ETHOOH",
         "ALD2",
         "HCOOH",
         "RCOOH",
         "C2O3",
         "PAN",
         "ARO1",
         "ARO2",
         "ALK1",
         "OLE1",
         "API1",
         "API2",
         "LIM1",
         "LIM2",
         "PAR",
         "AONE",
         "MGLY",
         "ETH",
         "OLET",
         "OLEI",
         "TOL",
         "XYL",
         "CRES",
         "TO2",
         "CRO",
         "OPEN",
         "ONIT",
         "ROOH",
         "RO2",
         "ANO2",
         "NAP",
         "XO2",
         "XPAR",
         "ISOP",
         "ISOPRD",
         "ISOPP",
         "ISOPN",
         "ISOPO2",
         "API",
         "LIM",
         "DMS",
         "MSA",
         "DMSO",
         "DMSO2",
         "CH3SO2H",
         "CH3SCH2OO",
         "CH3SO2",
         "CH3SO3",
         "CH3SO2OO",
         "CH3SO2CH2OO",
         "SULFHOX"))

    env_state = ppmc.EnvState(
        {
            "rel_humidity": 0.95,
            "latitude": 0,
            "longitude": 0,
            "altitude": 0 * si.m,
            "start_time": 21600 * si.s,
            "start_day": 200,
        }
    )

    aero_data = ppmc.AeroData(
        (
            #         density  ions in soln (1) molecular weight    kappa (1)
            #         |                     |   |                   |
            {"SO4": [1800 * si.kg / si.m**3, 1, 96.0 * si.g / si.mol, 0.00]},
            {"NO3": [1800 * si.kg / si.m**3, 1, 62.0 * si.g / si.mol, 0.00]},
            {"Cl": [2200 * si.kg / si.m**3, 1, 35.5 * si.g / si.mol, 0.00]},
            {"NH4": [1800 * si.kg / si.m**3, 1, 18.0 * si.g / si.mol, 0.00]},
            {"MSA": [1800 * si.kg / si.m**3, 0, 95.0 * si.g / si.mol, 0.53]},
            {"ARO1": [1400 * si.kg / si.m**3, 0, 150.0 * si.g / si.mol, 0.10]},
            {"ARO2": [1400 * si.kg / si.m**3, 0, 150.0 * si.g / si.mol, 0.10]},
            {"ALK1": [1400 * si.kg / si.m**3, 0, 140.0 * si.g / si.mol, 0.10]},
            {"OLE1": [1400 * si.kg / si.m**3, 0, 140.0 * si.g / si.mol, 0.10]},
            {"API1": [1400 * si.kg / si.m**3, 0, 184.0 * si.g / si.mol, 0.10]},
            {"API2": [1400 * si.kg / si.m**3, 0, 184.0 * si.g / si.mol, 0.10]},
            {"LIM1": [1400 * si.kg / si.m**3, 0, 200.0 * si.g / si.mol, 0.10]},
            {"LIM2": [1400 * si.kg / si.m**3, 0, 200.0 * si.g / si.mol, 0.10]},
            {"CO3": [2600 * si.kg / si.m**3, 1, 60.0 * si.g / si.mol, 0.00]},
            {"Na": [2200 * si.kg / si.m**3, 1, 23.0 * si.g / si.mol, 0.00]},
            {"Ca": [2600 * si.kg / si.m**3, 1, 40.0 * si.g / si.mol, 0.00]},
            {"OIN": [2600 * si.kg / si.m**3, 0, 1.0 * si.g / si.mol, 0.10]},
            {"OC": [1400 * si.kg / si.m**3, 0, 1.0 * si.g / si.mol, 0.10]},
            {"BC": [1800 * si.kg / si.m**3, 0, 1.0 * si.g / si.mol, 0.00]},
            {"H2O": [1000 * si.kg / si.m**3, 0, 18.0 * si.g / si.mol, 0.00]},
        )
    )

    gas_state = ppmc.GasState(gas_data)

    input_gas_state = (
        {"NO": [0.1E+00]},
        {"NO2": [1.0E+00]},
        {"HNO3": [1.0E+00]},
        {"O3": [5.0E+01]},
        {"H2O2": [1.1E+00]},
        {"CO": [2.1E+02]},
        {"SO2": [0.8E+00]},
        {"NH3": [0.5E+00]},
        {"HCl": [0.7E+00]},
        {"CH4": [2.2E+03]},
        {"C2H6": [1.0E+00]},
        {"HCHO": [1.2E+00]},
        {"CH3OH": [1.2E-01]},
        {"CH3OOH": [0.5E+00]},
        {"ALD2": [1.0E+00]},
        {"PAR": [2.0E+00]},
        {"AONE": [1.0E+00]},
        {"ETH": [0.2E+00]},
        {"OLET": [2.3E-02]},
        {"OLEI": [3.1E-04]},
        {"TOL": [0.1E+00]},
        {"XYL": [0.1E+00]},
        {"ONIT": [0.1E+00]},
        {"PAN": [0.8E+00]},
        {"RCOOH": [0.2E+00]},
        {"ROOH": [2.5E-02]},
        {"ISOP": [0.5E+00]}
    )

    gas_state.mix_rats = input_gas_state

    times = [0 * si.s]
    back_gas = [{"time": times},
                {"rate": [1.5e-5 / si.s]},
                {"NO": [0.1E+00]},
                {"NO2": [1.0E+00]},
                {"HNO3": [1.0E+00]},
                {"O3": [5.0E+01]},
                {"H2O2": [1.1E+00]},
                {"CO": [2.1E+02]},
                {"SO2": [0.8E+00]},
                {"NH3": [0.5E+00]},
                {"HCl": [0.7E+00]},
                {"CH4": [2.2E+03]},
                {"C2H6": [1.0E+00]},
                {"HCHO": [1.2E+00]},
                {"CH3OH": [1.2E-01]},
                {"CH3OOH": [0.5E+00]},
                {"ALD2": [1.0E+00]},
                {"PAR": [2.0E+00]},
                {"AONE": [1.0E+00]},
                {"ETH": [0.2E+00]},
                {"OLET": [2.3E-02]},
                {"OLEI": [3.1E-04]},
                {"TOL": [0.1E+00]},
                {"XYL": [0.1E+00]},
                {"ONIT": [0.1E+00]},
                {"PAN": [0.8E+00]},
                {"RCOOH": [0.2E+00]},
                {"ROOH": [2.5E-02]},
                {"ISOP": [0.5E+00]}
                ]

    gas_emit_times = [
        0,
        3600,
        7200,
        10800,
        14400,
        18000,
        21600,
        25200,
        28800,
        32400,
        36000,
        39600,
        43200,
        46800,
        50400,
        54000,
        57600,
        61200,
        64800,
        68400,
        72000,
        75600,
        79200,
        82800,
        90000,
        93600,
        97200,
        100800,
        104400,
        108000]

    gas_emit_rates = np.zeros(len(gas_emit_times))
    gas_emit_rates[0:12] = .5

    SO2 = [
        4.234E-09,
        5.481E-09,
        5.089E-09,
        5.199E-09,
        5.221E-09,
        5.284E-09,
        5.244E-09,
        5.280E-09,
        5.560E-09,
        5.343E-09,
        4.480E-09,
        3.858E-09,
        3.823E-09,
        3.607E-09,
        3.533E-09,
        3.438E-09,
        2.866E-09,
        2.667E-09,
        2.636E-09,
        2.573E-09,
        2.558E-09,
        2.573E-09,
        2.715E-09,
        3.170E-09,
        4.2344E-09,
        5.481E-09,
        5.089E-09,
        5.199E-09,
        5.221E-09,
        5.284E-09]

    NO2 = [
        3.024E-09,
        3.334E-09,
        3.063E-09,
        3.281E-09,
        3.372E-09,
        3.523E-09,
        3.402E-09,
        3.551E-09,
        3.413E-09,
        3.985E-09,
        3.308E-09,
        2.933E-09,
        2.380E-09,
        1.935E-09,
        1.798E-09,
        1.537E-09,
        9.633E-10,
        8.873E-10,
        7.968E-10,
        6.156E-10,
        5.920E-10,
        6.320E-10,
        9.871E-10,
        1.901E-09,
        3.024E-09,
        3.334E-09,
        3.063E-09,
        3.281E-09,
        3.372E-09,
        3.523E-09]

    NO = [
        5.749E-08,
        6.338E-08,
        5.825E-08,
        6.237E-08,
        6.411E-08,
        6.699E-08,
        6.468E-08,
        6.753E-08,
        6.488E-08,
        7.575E-08,
        6.291E-08,
        5.576E-08,
        4.524E-08,
        3.679E-08,
        3.419E-08,
        2.924E-08,
        1.832E-08,
        1.687E-08,
        1.515E-08,
        1.171E-08,
        1.125E-08,
        1.202E-08,
        1.877E-08,
        3.615E-08,
        5.749E-08,
        6.338E-08,
        5.825E-08,
        6.237E-08,
        6.411E-08,
        6.699E-08]

    CO = [
        7.839E-07,
        5.837E-07,
        4.154E-07,
        4.458E-07,
        4.657E-07,
        4.912E-07,
        4.651E-07,
        4.907E-07,
        6.938E-07,
        8.850E-07,
        8.135E-07,
        4.573E-07,
        3.349E-07,
        2.437E-07,
        2.148E-07,
        1.662E-07,
        8.037E-08,
        7.841E-08,
        6.411E-08,
        2.551E-08,
        2.056E-08,
        3.058E-08,
        1.083E-07,
        3.938E-07,
        7.839E-07,
        5.837E-07,
        4.154E-07,
        4.458E-07,
        4.657E-07,
        4.912E-07]

    NH3 = [
        8.93E-09,
        8.705E-09,
        1.639E-08,
        1.466E-08,
        1.6405E-08,
        1.8805E-08,
        1.65E-08,
        1.8045E-08,
        1.347E-08,
        6.745E-09,
        5.415E-09,
        2.553E-09,
        2.087E-09,
        2.2885E-09,
        2.7265E-09,
        2.7338E-09,
        9.96E-10,
        2.707E-09,
        9.84E-10,
        9.675E-10,
        9.905E-10,
        1.0345E-09,
        1.0825E-09,
        2.7465E-09,
        8.93E-09,
        8.705E-09,
        1.639E-08,
        1.466E-08,
        1.6405E-08,
        1.8805E-08]

    HCHO = [
        4.061E-09,
        3.225E-09,
        2.440E-09,
        2.639E-09,
        2.754E-09,
        2.888E-09,
        2.741E-09,
        2.885E-09,
        4.088E-09,
        5.186E-09,
        4.702E-09,
        2.601E-09,
        1.923E-09,
        1.412E-09,
        1.252E-09,
        9.776E-10,
        4.687E-10,
        4.657E-10,
        3.836E-10,
        1.717E-10,
        1.448E-10,
        1.976E-10,
        6.193E-10,
        2.090E-09,
        4.061E-09,
        3.225E-09,
        2.440E-09,
        2.639E-09,
        2.754E-09,
        2.888E-09]

    ALD2 = [
        1.702E-09,
        1.283E-09,
        9.397E-10,
        1.024E-09,
        1.076E-09,
        1.132E-09,
        1.068E-09,
        1.130E-09,
        1.651E-09,
        2.132E-09,
        1.985E-09,
        1.081E-09,
        7.847E-10,
        5.676E-10,
        5.003E-10,
        3.838E-10,
        1.784E-10,
        1.766E-10,
        1.430E-10,
        5.173E-11,
        4.028E-11,
        6.349E-11,
        2.428E-10,
        8.716E-10,
        1.7022E-09,
        1.283E-09,
        9.397E-10,
        1.024E-09,
        1.076E-09,
        1.132E-09]

    ETH = [
        1.849E-08,
        1.391E-08,
        1.010E-08,
        1.095E-08,
        1.148E-08,
        1.209E-08,
        1.142E-08,
        1.205E-08,
        1.806E-08,
        2.320E-08,
        2.149E-08,
        1.146E-08,
        8.384E-09,
        6.124E-09,
        5.414E-09,
        4.119E-09,
        1.953E-09,
        1.927E-09,
        1.575E-09,
        6.164E-10,
        4.973E-10,
        7.420E-10,
        2.653E-09,
        9.477E-09,
        1.849E-08,
        1.391E-08,
        1.010E-08,
        1.095E-08,
        1.148E-08,
        1.209E-08]

    OLEI = [
        5.948E-09,
        4.573E-09,
        3.374E-09,
        3.668E-09,
        3.851E-09,
        4.050E-09,
        3.841E-09,
        4.052E-09,
        6.094E-09,
        7.795E-09,
        7.215E-09,
        3.738E-09,
        2.718E-09,
        1.973E-09,
        1.729E-09,
        1.338E-09,
        6.333E-10,
        6.394E-10,
        5.126E-10,
        2.089E-10,
        1.708E-10,
        2.480E-10,
        8.947E-10,
        3.057E-09,
        5.948E-09,
        4.573E-09,
        3.374E-09,
        3.668E-09,
        3.851E-09,
        4.050E-09]

    OLET = [
        5.948E-09,
        4.573E-09,
        3.374E-09,
        3.668E-09,
        3.851E-09,
        4.050E-09,
        3.841E-09,
        4.052E-09,
        6.094E-09,
        7.795E-09,
        7.215E-09,
        3.738E-09,
        2.718E-09,
        1.973E-09,
        1.729E-09,
        1.338E-09,
        6.333E-10,
        6.394E-10,
        5.126E-10,
        2.089E-10,
        1.708E-10,
        2.480E-10,
        8.947E-10,
        3.057E-09,
        5.948E-09,
        4.573E-09,
        3.374E-09,
        3.668E-09,
        3.851E-09,
        4.050E-09]

    TOL = [
        6.101E-09,
        8.706E-09,
        7.755E-09,
        8.024E-09,
        8.202E-09,
        8.410E-09,
        8.218E-09,
        8.407E-09,
        1.020E-08,
        1.139E-08,
        7.338E-09,
        4.184E-09,
        3.078E-09,
        2.283E-09,
        2.010E-09,
        1.575E-09,
        8.966E-10,
        6.705E-10,
        5.395E-10,
        2.462E-10,
        2.106E-10,
        2.852E-10,
        9.300E-10,
        3.144E-09,
        6.101E-09,
        8.706E-09,
        7.755E-09,
        8.024E-09,
        8.202E-09,
        8.410E-09]

    XYL = [
        5.599E-09,
        4.774E-09,
        3.660E-09,
        3.909E-09,
        4.060E-09,
        4.239E-09,
        4.060E-09,
        4.257E-09,
        6.036E-09,
        7.448E-09,
        6.452E-09,
        3.435E-09,
        2.525E-09,
        1.859E-09,
        1.650E-09,
        1.302E-09,
        6.852E-10,
        6.773E-10,
        5.437E-10,
        2.697E-10,
        2.358E-10,
        3.059E-10,
        8.552E-10,
        2.861E-10,
        5.599E-09,
        4.774E-09,
        3.660E-09,
        3.909E-09,
        4.060E-09,
        4.239E-09]

    AONE = [
        7.825E-10,
        2.858E-09,
        2.938E-09,
        2.947E-09,
        2.948E-09,
        2.951E-09,
        2.947E-09,
        2.954E-09,
        3.032E-09,
        2.766E-09,
        1.313E-09,
        1.015E-09,
        8.363E-10,
        7.040E-10,
        6.404E-10,
        6.264E-10,
        5.661E-10,
        1.538E-10,
        1.500E-10,
        1.395E-10,
        1.476E-10,
        1.503E-10,
        2.256E-10,
        4.244E-10,
        7.825E-10,
        2.858E-09,
        2.938E-09,
        2.947E-09,
        2.948E-09,
        2.951E-09]

    PAR = [
        1.709E-07,
        1.953E-07,
        1.698E-07,
        1.761E-07,
        1.808E-07,
        1.865E-07,
        1.822E-07,
        1.8599E-07,
        2.412E-07,
        2.728E-07,
        2.174E-07,
        1.243E-07,
        9.741E-08,
        7.744E-08,
        6.931E-08,
        5.805E-08,
        3.900E-08,
        3.317E-08,
        2.956E-08,
        2.306E-08,
        2.231E-08,
        2.395E-08,
        4.284E-08,
        9.655E-08,
        1.709E-07,
        1.953E-07,
        1.698E-07,
        1.761E-07,
        1.808E-07,
        1.865E-07]

    ISOP = [
        2.412E-10,
        2.814E-10,
        3.147E-10,
        4.358E-10,
        5.907E-10,
        6.766E-10,
        6.594E-10,
        5.879E-10,
        5.435E-10,
        6.402E-10,
        5.097E-10,
        9.990E-11,
        7.691E-11,
        5.939E-11,
        5.198E-11,
        4.498E-11,
        3.358E-11,
        2.946E-11,
        2.728E-11,
        2.183E-11,
        1.953E-11,
        1.890E-11,
        2.948E-11,
        1.635E-10,
        2.412E-10,
        2.814E-10,
        3.147E-10,
        4.358E-10,
        5.907E-10,
        6.766E-10]

    CH3OH = [
        2.368E-10,
        6.107E-10,
        6.890E-10,
        6.890E-10,
        6.890E-10,
        6.889E-10,
        6.886E-10,
        6.890E-10,
        6.890E-10,
        5.414E-10,
        3.701E-10,
        2.554E-10,
        1.423E-10,
        6.699E-11,
        2.912E-11,
        2.877E-11,
        2.825E-11,
        2.056E-12,
        2.056E-12,
        2.056E-12,
        2.435E-12,
        2.435E-12,
        4.030E-11,
        1.168E-10,
        2.368E-10,
        6.107E-10,
        6.890E-10,
        6.890E-10,
        6.890E-10,
        6.889E-10]

    ANOL = [
        5.304E-09,
        7.960E-09,
        7.649E-09,
        7.649E-09,
        7.432E-09,
        7.428E-09,
        7.431E-09,
        7.434E-09,
        7.434E-09,
        6.979E-09,
        5.666E-09,
        4.361E-09,
        4.148E-09,
        3.289E-09,
        2.858E-09,
        2.856E-09,
        1.127E-09,
        9.615E-10,
        9.616E-10,
        9.616E-10,
        9.654E-10,
        9.654E-10,
        1.397E-09,
        2.264E-09,
        5.304E-09,
        7.960E-09,
        7.649E-09,
        7.649E-09,
        7.432E-09,
        7.428E-09]

    emit_gas = [
        {"time": gas_emit_times},
        {"rate": list(gas_emit_rates)},
        {"SO2": SO2},
        {"NO": NO},
        {"NO2": NO2},
        {"CO": CO},
        {"NH3": NH3},
        {"HCHO": HCHO},
        {"ALD2": ALD2},
        {"ETH": ETH},
        {"OLEI": OLEI},
        {"OLET": OLET},
        {"TOL": TOL},
        {"XYL": XYL},
        {"AONE": AONE},
        {"PAR": PAR},
        {"ISOP": ISOP},
        {"CH3OH": CH3OH},
        {"ANOL": ANOL},
    ]

    AERO_DIST_BACKGROUND = {
        "back_small": {
            "mass_frac": [{"SO4": [1]}, {"OC": [1.375]}, {"NH4": [0.375]}],
            "diam_type": "geometric",
            "mode_type": "log_normal",
            "num_conc": 3.2e9 / si.m**3,
            "geom_mean_diam": 0.02 * si.um,
            "log10_geom_std_dev": 0.161,
        },
        "back_large": {
            "mass_frac": [{"SO4": [1]}, {"OC": [1.375]}, {"NH4": [0.375]}],
            "diam_type": "geometric",
            "mode_type": "log_normal",
            "num_conc": 2.9e9 / si.m**3,
            "geom_mean_diam": 0.16 * si.um,
            "log10_geom_std_dev": 0.217,
        },
    }

    AERO_DIST_EMIT = {
        "gasoline": {
            "mass_frac": [{"OC": [0.8]}, {"BC": [0.2]}],
            "diam_type": "geometric",
            "mode_type": "log_normal",
            "num_conc": 5e7 / si.m**3,
            "geom_mean_diam": 5e-8 * si.m,
            "log10_geom_std_dev": 0.24,
        },
        "diesel": {
            "mass_frac": [{"OC": [0.3]}, {"BC": [0.7]}],
            "diam_type": "geometric",
            "mode_type": "log_normal",
            "num_conc": 1.6e8 / si.m**3,
            "geom_mean_diam": 5e-8 * si.m,
            "log10_geom_std_dev": 0.24,
        },
        "cooking": {
            "mass_frac": [{"OC": [1]}],
            "diam_type": "geometric",
            "mode_type": "log_normal",
            "num_conc": 9e6 / si.m**3,
            "geom_mean_diam": 8.64e-8 * si.m,
            "log10_geom_std_dev": 0.28,
        },
    }

    time_timeseries = list(np.linspace(0, 24 * 3600, 25))
    pressure_timeseries = list(np.ones(25) * 1e5)
    temp_timeseries = [
        290.016,
        292.5,
        294.5,
        296.112,
        297.649,
        299.049,
        299.684,
        299.509,
        299.002,
        298.432,
        296.943,
        295.153,
        293.475,
        292.466,
        291.972,
        291.96,
        291.512,
        291.481,
        290.5,
        290.313,
        290.317,
        290.362,
        290.245,
        290.228,
        291.466]
    height_timeseries = [
        171.045,
        228.210,
        296.987,
        366.002,
        410.868,
        414.272,
        417.807,
        414.133,
        397.465,
        376.864,
        364.257,
        352.119,
        338.660,
        322.028,
        305.246,
        258.497,
        240.478,
        187.229,
        145.851,
        128.072,
        110.679,
        97.628,
        93.034,
        93.034,
        93.034]

    scenario = ppmc.Scenario(
        gas_data,
        aero_data,
        {
            "temp_profile": [{"time": time_timeseries}, {"temp": temp_timeseries}],
            "pressure_profile": [
                {"time": time_timeseries},
                {"pressure": pressure_timeseries},
            ],
            "height_profile": [{"time": time_timeseries}, {"height": height_timeseries}],
            "gas_emissions": emit_gas,
            "gas_background": back_gas,
            "aero_emissions": [
                {"time": [0 * si.s, 12 * 3600 * si.s]},
                {"rate": [1 / si.s, 0 / si.s]},
                {"dist": [[AERO_DIST_EMIT], [AERO_DIST_EMIT]]},
            ],
            "aero_background": [
                {"time": [0 * si.s]},
                {"rate": [1.5e-5 / si.s]},
                {"dist": [[AERO_DIST_BACKGROUND]]},
            ],
            "loss_function": "none",
        },
    )

    T_INITIAL = 0.0
    scenario.init_env_state(env_state, T_INITIAL)

    AERO_DIST_INIT = [
        {
            "init_small": {
                "mass_frac": [{"SO4": [1]}, {"OC": [1.375]}, {"NH4": [0.375]}],
                "diam_type": "geometric",
                "mode_type": "log_normal",
                "num_conc": 3.2e9 / si.m**3,
                "geom_mean_diam": 0.02 * si.um,
                "log10_geom_std_dev": 0.161,
            },
            "init_large": {
                "mass_frac": [{"SO4": [1]}, {"OC": [1.375]}, {"NH4": [0.375]}],
                "diam_type": "geometric",
                "mode_type": "log_normal",
                "num_conc": 2.9e9 / si.m**3,
                "geom_mean_diam": 0.16 * si.um,
                "log10_geom_std_dev": 0.217,
            },
        }
    ]

    aero_dist_init = ppmc.AeroDist(aero_data, AERO_DIST_INIT)

    run_part_opt = ppmc.RunPartOpt(
        {
            "output_prefix": f"/partmc/partmc-volume/{session_id}/result",
            "do_coagulation": True,
            "coag_kernel": "brown",
            "t_max": 86400 * si.s,
            "del_t": 60 * si.s,
            "t_output": 3600.0,
        }
    )

    N_PART = 1000
    aero_state = ppmc.AeroState(aero_data, N_PART, 'nummass_source')
    aero_state.dist_sample(
        aero_dist_init,
        sample_prop=1.0,
        create_time=0.0,
        allow_doubling=True,
        allow_halving=True,
    )

    camp_core = ppmc.CampCore()
    photolysis = ppmc.Photolysis()

    ppmc.run_part(
        scenario,
        env_state,
        aero_data,
        aero_state,
        gas_data,
        gas_state,
        run_part_opt,
        camp_core,
        photolysis,
    )
