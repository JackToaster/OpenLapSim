import BatterySim
import csv
import matplotlib.pyplot as plt


def read_battery_data(file_path):
    time_seconds = []
    battery_data = []

    # Open the CSV file and read its contents
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            time_minutes = float(row['Time (Minutes)'])
            voltage = float(row['Cell Voltage'])
            current = float(row['Cell current (A)'])
            anode_temp = float(row['Anode temp'])
            cathode_temp = float(row['Cathode temp'])
            soc = current  # Assuming SOC is directly related to current (you can adjust this)

            # Convert time to seconds
            time_seconds.append(time_minutes * 60.0)

            # Create BatterySimOutput object and append to battery_data
            battery_output = BatterySim.BatterySimOutput(t_internal=cathode_temp, t_anode=anode_temp, soc=0, voltage=voltage, current=current, rint=0)  # Replace 0.0 with actual rint
            battery_data.append(battery_output)

    return time_seconds, battery_data


def plot_test_data(test_results, sim_results, times):
    # Extract data from the results
    test_t_cathode = [result.t_internal for result in test_results]
    test_t_anode = [result.t_anode for result in test_results]
    test_v = [result.voltage for result in test_results]
    test_current = [result.current for result in test_results]

    t_internal_values = [result.t_internal for result in sim_results]
    t_anode_values = [result.t_anode for result in sim_results]
    soc_values = [result.soc for result in sim_results]
    voltage_values = [result.voltage for result in sim_results]
    current_values = [result.current for result in sim_results]
    rint_values = [result.rint for result in sim_results]

    # Create subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle('Transient Thermal Simulation Results')

    ax1 = axs[1]
    # Plot Voltage, Rint, and Current on separate y-axes
    color = 'tab:blue'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage', color=color)
    ax1.plot(times, test_v, label='Test Voltage', color=color)
    ax1.plot(times, voltage_values, label='Sim Voltage', color="tab:cyan")
    ax1.tick_params(axis='y', labelcolor=color)

    # Create a second y-axis for Current
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Current', color=color)
    ax2.plot(times, test_current, label='Test Current', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # Add legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    # Plot Temperatures and SOC on the same subplot with separate y-axes
    ax0 = axs[0]
    ax0.set_xlabel('Time (s)')
    ax0.set_ylabel('Temperatures (°C)')
    ax0.plot(times, test_t_cathode, label='t_cathode', color='tab:blue')
    ax0.plot(times, test_t_anode, label='t_anode', color='tab:green')
    ax0.plot(times, t_internal_values, label='Sim t_internal', color='tab:cyan')
    ax0.plot(times, t_anode_values, label='Sim t_anode', color='tab:olive')
    ax0.tick_params(axis='y', labelcolor='tab:blue')

    lines, labels = ax0.get_legend_handles_labels()
    ax0.legend(lines, labels, loc='upper left')

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    # Show the plots
    plt.show()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    times, test_results = read_battery_data(file_path)

    current_values = [result.current for result in test_results]

    bm = BatterySim.BatteryModel(initial_temperature=test_results[0].t_anode, initial_soc=0.7, series_cells=1)

    sim_results = []

    # To make things match up:
    print(current_values[0])

    sim_results.append(bm.update_current(current_values[0], 0.1))

    for i in range(len(times) - 1):
        t_start = times[i]
        t_end = times[i+1]
        current_start = current_values[i]
        current_end = current_values[i+1]
        avg_current = (current_start + current_end) / 2
        res = bm.update_current(avg_current, t_end - t_start)

        sim_results.append(res)

    plot_test_data(test_results, sim_results, times)
