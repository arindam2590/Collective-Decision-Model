import os
from Environment.SimEnv import SimEnv
from Utils.config import setup_perser, set_params
from Utils.utils import (
    display_simulation_config,
    simulation_init,
    read_from_file,
    plot_performance_graph,
    _avg_mismatch_series,
    _avg_collision_series,
    _avg_phase_series,
    _avg_accuracy_series,
    append_metrics_to_csv,
    append_reached_timeseries,        # NEW
    plot_figures_from_csv,            # direction mismatch
    plot_collision_figures_from_csv,  # collisions
    plot_phase_figures_from_csv,      # kuramoto-only phase
    plot_reached_figures_from_csv,    # NEW: agents reached per time step
    _ensure_data_dir,
)
from Model.CollectiveDecisionModel import MajorityRuleModel, VoterModel, KuramotoModel


def _run_one(params, model_key, max_steps=0):
    """
    Run one model configuration and return averaged metric series + per-step reached counts.
    """
    # (Re)generate initial conditions for this run
    simulation_init(params)
    data_list = read_from_file()
    agent_pos = [tuple(e) for e in data_list[0]]
    targets   = [tuple(e) for e in data_list[1]]
    hurdles   = [tuple(e) for e in data_list[2]]

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
    # Grab per-timestep reached counts BEFORE closing
    reached_counts = list(simEnv.reached_counts)
    simEnv.close_sim()

    # Average series per checkpoint for the legacy CSV
    return (pretty,
            _avg_mismatch_series(perf),
            _avg_collision_series(perf),
            _avg_phase_series(perf),
            _avg_accuracy_series(perf),
            reached_counts)


def _batch_sweep(args):
    """
    Sweep: agents {10,20,30,40} × targets {2,10} × models {majority,voter,kuramoto}
    Save per-checkpoint averages to the main CSV, and per-time-step agents-reached
    to Data/reached_timeseries.csv.
    """
    env0, sw0 = set_params()
    agent_sizes  = [10, 20, 30, 40]
    target_sizes = [2, 10]
    model_keys   = ['majority', 'voter', 'kuramoto']

    # Headless display/audio for batch runs
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    _ensure_data_dir()

    from Utils.utils import _ensure_csv_with_header
    _ensure_csv_with_header(args.csv_out)

    for A in agent_sizes:
        for T in target_sizes:
            # Fresh params for this (A, T)
            env = dict(env0)
            swarm = dict(sw0)
            swarm['NUM_AGENTS'] = A
            env['NUM_TARGET']   = T
            params = [env, swarm]

            for mk in model_keys:
                name, mis, col, phs, acc, reached = _run_one(params, mk, max_steps=args.max_steps)

                # Legacy checkpoint CSV (unchanged)
                append_metrics_to_csv(args.csv_out, A, T, name, mis, col, phs, acc)

                # NEW: per-time-step agents reached CSV
                append_reached_timeseries(A, T, name, reached)

                print(f"Saved: A={A}, T={T}, model={name}, checkpoints={len(mis)}, steps={len(reached)}")

    print(f"\nSweep complete. CSV: {args.csv_out}")
    print("Agents-reached timeseries: Data/reached_timeseries.csv")
    print(f"Direction mismatch figs:\n  python main.py --plot-only --csv-in {args.csv_out}")
    print(f"Collision figs:\n  python main.py --plot-collision --csv-in {args.csv_out}")
    print(f"Phase-sync figs (Kuramoto):\n  python main.py --plot-phase --csv-in {args.csv_out}")
    print(f"Agents-reached figs:\n  python main.py --plot-accuracy")  # reuse flag to avoid new CLI param


def main():
    args = setup_perser()

    # --- Plot-only branches (no simulation) ---
    if getattr(args, 'plot_only', False):
        plot_figures_from_csv(args.csv_in)  # direction mismatch
        print("Figures written to Data/DirectionMismatch_*A_2T_vs_10T.png")
        return

    if getattr(args, 'plot_collision', False):
        plot_collision_figures_from_csv(args.csv_in)  # collision
        print("Figures written to Data/Collision_*A_2T_vs_10T.png")
        return

    if getattr(args, 'plot_phase', False):
        plot_phase_figures_from_csv(args.csv_in)  # phase sync (Kuramoto)
        print("Figures written to Data/PhaseSync_*A_2T_vs_10T.png")
        return

    # Reuse --plot-accuracy to plot the *new* per-time-step counts
    if getattr(args, 'plot_accuracy', False):
        plot_reached_figures_from_csv('Data/reached_timeseries.csv')
        print("Figures written to Data/AgentsReached_*A_2T_vs_10T.png")
        return

    # --- Batch sweep ---
    if getattr(args, 'batch', False):
        _batch_sweep(args)
        return

    # --- Single-run (interactive window) ---
    params = set_params()

    print('\n')
    print('%' * 60)
    if getattr(args, 'newdata', False):
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

    # Choose model by flags; default to Majority to avoid None crash
    if getattr(args, 'majority', False):
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)
    elif getattr(args, 'voter', False):
        simEnv.model = VoterModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)
    elif getattr(args, 'kuramoto', False):
        simEnv.model = KuramotoModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)
    else:
        print('No model selected via CLI, defaulting to Majority Model (-m).')
        simEnv.model = MajorityRuleModel(agent_pos, targets, params)
        print('Model Select :', simEnv.model.Name)

    performance_data = simEnv.run_simulation(
        hurdles,
        targets,
        max_steps=getattr(args, 'max_steps', 0)
    )
    plot_performance_graph(simEnv.model.Name, performance_data, params)
    simEnv.close_sim()


if __name__ == "__main__":
    main()
