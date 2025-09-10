import os
from Environment.SimEnv import SimEnv
from Utils.config import setup_perser, set_params
from Utils.utils import (
    display_simulation_config, simulation_init, read_from_file, plot_performance_graph,
    _avg_mismatch_series, append_series_to_csv, plot_figures_from_csv, _ensure_data_dir
)
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel

def _run_one(params, model_key, max_steps):
    """Run one model with current params; return (pretty_model_name, avg_series)."""
    simulation_init(params)  # creates Data/data.txt with positions/targets/hurdles
    data_list = read_from_file()
    agent_pos = [tuple(e) for e in data_list[0]]
    targets   = [tuple(e) for e in data_list[1]]
    hurdles   = [tuple(e) for e in data_list[2]]

    simEnv = SimEnv(params, targets)

    if model_key == 'majority':
        simEnv.model = MajorityRuleModel(agent_pos, targets, params); pretty = 'Majority Model'
    elif model_key == 'voter':
        simEnv.model = VoterModel(agent_pos, targets, params);         pretty = 'Voter Model'
    elif model_key == 'kuramoto':
        simEnv.model = KuramotoModel(agent_pos, targets, params);      pretty = 'Kuramoto Model'
    else:
        raise ValueError(f'Unknown model_key: {model_key}')

    perf = simEnv.run_simulation(hurdles, targets, max_steps=max_steps)  # SimEnv already supports max_steps
    simEnv.close_sim()
    return pretty, _avg_mismatch_series(perf)

def _batch_sweep(args):
    """agents {10,20,30,40} × targets {2,10} × models {majority,voter,kuramoto} → CSV."""
    env0, sw0 = set_params()
    agent_sizes  = [10, 20, 30, 40]
    target_sizes = [2, 10]
    model_keys   = ['majority', 'voter', 'kuramoto']

    # force headless for batch so no windows pop
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    _ensure_data_dir()  # Data/

    # ensure CSV header (append-only)
    from Utils.utils import _ensure_csv_with_header
    _ensure_csv_with_header(args.csv_out)

    for A in agent_sizes:
        for T in target_sizes:
            env = dict(env0); swarm = dict(sw0)
            swarm['NUM_AGENTS'] = A
            env['NUM_TARGET']   = T
            params = [env, swarm]

            for mk in model_keys:
                model_name, series = _run_one(params, mk, max_steps=args.max_steps)
                append_series_to_csv(args.csv_out, A, T, model_name, series)
                print(f"Saved: A={A}, T={T}, model={model_name}, checkpoints={len(series)}")

    print(f"\nSweep complete. CSV: {args.csv_out}")
    print(f"Now build figures:\n  python main.py --plot-only --csv-in {args.csv_out}")

# ---------------- main entry ----------------
def main():
    # Plot-only branch: read CSV → make 4 figures (2 subplots each, 3 lines)
    if args.plot_only:
        plot_figures_from_csv(args.csv_in)
        print("Figures written to Data/Compare_*A_2T_vs_10T.png")
        return

    # Batch branch
    if args.batch:
        _batch_sweep(args)
        return

    # ---------- normal single run ----------
    params = set_params()

    print('\n')
    print('%' * 60)
    if args.newdata:
        is_new_data = True;  print('Simulation has been started with New Data')
    else:
        is_new_data = False; print('Simulation has been started with Old Data')

    # optional headless for single run
    if not args.render:
        os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

    display_simulation_config(params)
    if is_new_data:
        simulation_init(params)

    data_list = read_from_file()
    agent_pos = [tuple(e) for e in data_list[0]]
    targets   = [tuple(e) for e in data_list[1]]
    hurdles   = [tuple(e) for e in data_list[2]]

    simEnv = SimEnv(params, targets)
    if args.majority:
        simEnv.model = MajorityRuleModel(agent_pos, targets, params); print('Model Select :', simEnv.model.Name)
    elif args.voter:
        simEnv.model = VoterModel(agent_pos, targets, params);         print('Model Select : ', simEnv.model.Name)
    elif args.kuramoto:
        simEnv.model = KuramotoModel(agent_pos, targets, params);      print('Model Select : ', simEnv.model.Name)
    else:
        print('No Model is selected')

    perf = simEnv.run_simulation(hurdles, targets, max_steps=args.max_steps)
    plot_performance_graph(simEnv.model.Name, perf, params)
    simEnv.close_sim()

if __name__ == "__main__":
    args = setup_perser()
    main()
