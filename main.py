import os
from Environment.SimEnv import SimEnv
from Utils.config import setup_perser, set_params
from Utils.utils import (
    display_simulation_config, simulation_init, read_from_file, plot_performance_graph,
    _avg_mismatch_series, _avg_collision_series, append_metrics_to_csv,
    plot_figures_from_csv, plot_collision_figures_from_csv, _ensure_data_dir
)
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel


def _run_one(params, model_key, max_steps):
    """Run one model; return (pretty_name, avg_mismatch_series, avg_collision_series)."""
    simulation_init(params)
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

    perf = simEnv.run_simulation(hurdles, targets, max_steps=max_steps)
    simEnv.close_sim()

    return pretty, _avg_mismatch_series(perf), _avg_collision_series(perf)


def _batch_sweep(args):
    """
    agents {10,20,30,40} × targets {2,10} × models {majority,voter,kuramoto} → CSV
    (saves both avg_dir_mismatch and avg_collisions per checkpoint)
    """
    env0, sw0 = set_params()
    agent_sizes  = [10, 20, 30, 40]
    target_sizes = [2, 10]
    model_keys   = ['majority', 'voter', 'kuramoto']

    # Headless so many runs don't pop windows
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    _ensure_data_dir()

    from Utils.utils import _ensure_csv_with_header
    _ensure_csv_with_header(args.csv_out)

    for A in agent_sizes:
        for T in target_sizes:
            env = dict(env0); swarm = dict(sw0)
            swarm['NUM_AGENTS'] = A
            env['NUM_TARGET']   = T
            params = [env, swarm]

            for mk in model_keys:
                name, mis, col = _run_one(params, mk, max_steps=args.max_steps)
                append_metrics_to_csv(args.csv_out, A, T, name, mis, col)
                print(f"Saved: A={A}, T={T}, model={name}, checkpoints={len(mis)}")

    print(f"\nSweep complete. CSV: {args.csv_out}")
    print(f"Now build figures (direction mismatch):\n  python main.py --plot-only --csv-in {args.csv_out}")
    print(f"Or build collision figures:\n  python main.py --plot-collision --csv-in {args.csv_out}")


def main():
    # Plot-only branches (no simulation)
    if args.plot_only:
        plot_figures_from_csv(args.csv_in)  # direction mismatch
        print("Figures written to Data/Compare_*A_2T_vs_10T.png")
        return

    if args.plot_collision:
        plot_collision_figures_from_csv(args.csv_in)  # collisions
        print("Figures written to Data/Collision_*A_2T_vs_10T.png")
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
        is_new_data = True
        print('Simulation has been started with New Data')
    else:
        is_new_data = False
        print('Simulation has been started with Old Data')

    display_simulation_config(params)
    if is_new_data:
        simulation_init(params)

    data_list = read_from_file()
    agent_pos = [tuple(element) for element in data_list[0]]
    targets   = [tuple(element) for element in data_list[1]]
    hurdles   = [tuple(element) for element in data_list[2]]

    simEnv = SimEnv(params, targets)
    if args.majority:
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)
    elif args.voter:
        simEnv.model = VoterModel(agent_pos, targets, params)
        print('Model Select : ', simEnv.model.Name)
    elif args.kuramoto:
        simEnv.model = KuramotoModel(agent_pos, targets, params)
        print('Model Select : ', simEnv.model.Name)
    else:
        print('No Model is selected')

    performance_data = simEnv.run_simulation(hurdles, targets, max_steps=args.max_steps if hasattr(args, 'max_steps') else 0)
    plot_performance_graph(simEnv.model.Name, performance_data, params)
    simEnv.close_sim()


if __name__ == "__main__":
    args = setup_perser()
    main()
