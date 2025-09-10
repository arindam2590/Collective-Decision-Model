from Environment.SimEnv import SimEnv
from Utils.config import setup_perser, set_params
from Utils.utils import (
    display_simulation_config,
    simulation_init,
    read_from_file,
    plot_performance_graph,
    _avg_mismatch_series,
    append_series_to_csv,
    plot_figures_from_csv,
)
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel
import os


def _run_one(params, model_key, max_steps):
    """Run one model on current params; return (pretty_model_name, avg_series)."""
    # fresh data for this param set
    simulation_init(params)
    data_list = read_from_file()
    agent_pos = [tuple(e) for e in data_list[0]]
    targets = [tuple(e) for e in data_list[1]]
    hurdles = [tuple(e) for e in data_list[2]]

    simEnv = SimEnv(params, targets)

    if model_key == 'majority':
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
        pretty = 'Majority Model'
    elif model_key == 'voter':
        simEnv.model = VoterModel(agent_pos, targets, params)
        pretty = 'Voter Model'
    elif model_key == 'kuramoto':
        simEnv.model = KuramotoModel(agent_pos, targets, params)
        pretty = 'Kuramoto Model'
    else:
        raise ValueError(f'Unknown model_key: {model_key}')

    perf = simEnv.run_simulation(hurdles, targets, max_steps=max_steps)
    simEnv.close_sim()
    return pretty, _avg_mismatch_series(perf)


def _batch_sweep(args):
    """
    agents in {10,20,30,40}, targets in {2,10}, models = [majority, voter, kuramoto].
    Save every run to CSV (agents, targets, model, checkpoint, avg_dir_mismatch).
    """
    env0, sw0 = set_params()
    agent_sizes = [10, 20, 30, 40]
    target_sizes = [2, 10]
    model_keys = ['majority', 'voter', 'kuramoto']

    # headless display so many runs don't pop windows
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

    # ensure CSV header exists; DO NOT truncate inside the loop
    from Utils.utils import _ensure_csv_with_header
    _ensure_csv_with_header(args.csv_out)

    for A in agent_sizes:
        for T in target_sizes:
            env = dict(env0)
            swarm = dict(sw0)
            swarm['NUM_AGENTS'] = A
            env['NUM_TARGET'] = T
            params = [env, swarm]

            for mk in model_keys:
                model_name, series = _run_one(params, mk, max_steps=args.max_steps)
                append_series_to_csv(args.csv_out, A, T, model_name, series)
                print(f"Saved: A={A}, T={T}, model={model_name}, checkpoints={len(series)}")

    print(f"\nSweep complete. CSV: {args.csv_out}")
    print(f"Now build figures from CSV:\n  python main.py --plot-only --csv-in {args.csv_out}")


def main():
    # Plot-only branch: just read CSV and make figures
    if args.plot_only:
        plot_figures_from_csv(args.csv_in)
        print("Figures written to Data/Compare_*A_2T_vs_10T.png")
        return

    # Batch sweep branch
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
    targets = [tuple(element) for element in data_list[1]]
    hurdles = [tuple(element) for element in data_list[2]]

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

    performance_data = simEnv.run_simulation(hurdles, targets, max_steps=args.max_steps)
    plot_performance_graph(simEnv.model.Name, performance_data, params)
    simEnv.close_sim()


if __name__ == "__main__":
    args = setup_perser()
    main()
