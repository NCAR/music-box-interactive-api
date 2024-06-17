from api.controller import get_model_run
import os
import numpy as np
import PyPartMC as ppmc
from PyPartMC import si

# Here are all the default configurations, which will be overwritten by
# the netcdfs
N_TIMES = 25
rh = np.zeros(N_TIMES)
time = np.zeros(N_TIMES)
AERO_DATA_CTOR_ARG_MINIMAL = (
    {"H2O": [1000 * si.kg / si.m**3, 1, 18e-3 * si.kg / si.mol, 0]},
)
AERO_STATE_CTOR_ARG_MINIMAL = (0, "nummass_source")
GAS_DATA_CTOR_ARG_MINIMAL = ("SO2",)
ENV_STATE_CTOR_ARG_MINIMAL = {
    "rel_humidity": 0.0,
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "start_time": 44.0,
    "start_day": 0,
}

aero_data = ppmc.AeroData(AERO_DATA_CTOR_ARG_MINIMAL)
aero_state = ppmc.AeroState(aero_data, *AERO_STATE_CTOR_ARG_MINIMAL)
gas_data = ppmc.GasData(GAS_DATA_CTOR_ARG_MINIMAL)
gas_state = ppmc.GasState(gas_data)
env_state = ppmc.EnvState(ENV_STATE_CTOR_ARG_MINIMAL)


# Get the concentration of number and mass
def get_concentration(session_id):
    model = get_model_run(session_id)
    if 'partmc_output_path' in model.results:
        output_dir = model.results['partmc_output_path']
        num_conc = np.zeros(N_TIMES)
        mass_conc = np.zeros(N_TIMES)
        for i_time in range(N_TIMES):
            path = os.path.join(output_dir, f'result_0001_{i_time+1:08}.nc')
            filename = ppmc.input_state(
                path, aero_data, aero_state, gas_data, gas_state, env_state)
            num_conc[i_time] = aero_state.total_num_conc
            mass_conc[i_time] = aero_state.total_mass_conc
            time[i_time] = env_state.elapsed_time + env_state.start_time
        num_list = num_conc.tolist()
        mass_list = mass_conc.tolist()
        time_list = time.tolist()
        dict = {
            'time': time_list,
            'number_conc': num_list,
            'mass_conc': mass_list}
        return dict
    else:
        return {}
