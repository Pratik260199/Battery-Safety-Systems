###############################################################################
# Name: Ryan Soltis
# Date: 6/24/2021
# For Whom: Li-Ion Summer Research
# Description: Test code to determine functionalitity of PyBaMM and to allow
# user to gain experience with interface.
###############################################################################

################################ Libraries ####################################
import pybamm as bam
import os

###############################################################################


# Tutorial_1 runs through a single simulation and outputs a single set of plots
def Tutorial_1():
    model = bam.lithium_ion.DFN()
    sim = bam.Simulation(model)
    result = sim.solve([0,3600])
    graph = sim.plot()
    
    return()


# Tutorial_2 runs three different simulations and produces a distince set of 
# plots for each (3 total sets)
def Tutorial_2():
    models = [
        bam.lithium_ion.SPM(),
        bam.lithium_ion.SPMe(),
        bam.lithium_ion.DFN()
        ]

    sims = []
    for model in models:
        sim = bam.Simulation(model)
        sim.solve([0,3600])
        sims.append(sim)
        bam.dynamic_plot(sim, time_unit='seconds')
        
    return()

# Tutorial_3 runs through plotting individual plots from the large set from Tutorial_1
def Tutorial_3():
    model = bam.lithium_ion.DFN()
    sim = bam.Simulation(model)
    result = sim.solve([0,3600])
    output_variables = ["Electrolyte concentration [mol.m-3]","Terminal voltage [V]"]
    sim.plot(output_variables = output_variables)
    

    return()

# Tutorial_4 runs through changing parameter values when running simulations
def Tutorial_4():
    chemistry = bam.parameter_sets.Chen2020
    parameter_values = bam.ParameterValues(chemistry=chemistry)    
    
    model = bam.lithium_ion.DFN()
    sim = bam.Simulation(model, parameter_values=parameter_values)
    sim.solve([0, 3600])
    sim.plot()
    
    # Changing Values (Amps set to 10)
    model = bam.lithium_ion.DFN()
    parameter_values = bam.ParameterValues(chemistry=bam.parameter_sets.Chen2020)
    parameter_values["Current function [A]"] = 10
    sim = bam.Simulation(model, parameter_values=parameter_values)
    sim.solve([0, 3600])
    sim.plot()
    
    return()

# Tutorial_5 runs through setting up and running an experiment
# For experiment instruction syntax, visit: https://colab.research.google.com/
# github/pybamm-team/PyBaMM/blob/main/examples/notebooks/Getting%20Started/
# Tutorial%205%20-%20Run%20experiments.ipynb
def Tutorial_5():
    experiment = bam.Experiment(
        [
            ('Discharge at C/10 for 10 hours or until 3.3 V',
             'Rest for 1 hour',
             'Charge at 1 A until 4.1 V',
             'Hold at 4.1 V until 50 mA',
             'Rest for 1 hour'),
        ] * 3
    )
    
    model = bam.lithium_ion.DFN()
    sim = bam.Simulation(model, experiment = experiment)
    sim.solve()
    sim.plot()
    
    return()

# Tutorial_6 runs a simulation and save the result as either a pkl, csv, or 
# mat file in the same directory as this script
def Tutorial_6():
    model = bam.lithium_ion.SPMe()
    sim = bam.Simulation(model)
    sim.solve([0, 3600])
    
    solution = sim.solution
    t = solution['Time [s]']
    V = solution['Terminal voltage [V]']
    
    V.entries
    t.entries
    V([200, 400, 780, 1236])
    
    # SAving simulation data
    sim.save('SPMe.pkl')
    sim2 = bam.load('SPMe.pkl')
    sim2.plot()
    
    sol = sim.solution
    sol.save('SPMe_sol.pkl')
    
    sol2 = bam.load("SPMe_sol.pkl")
    bam.dynamic_plot(sol2)
    
    # Saving as csv
    sol.save_data("sol_data.csv", ['Current [A]', 'Terminal voltage [V]'], 
                                   to_format='csv')
    
    # SAving as matlab
    sol.save_data("sol_data.mat", ['Current [A]', 'Terminal voltage [V]'],
                 to_format="matlab", short_names={'Current [A]': "I", 
                                                  'Terminal voltage [V]': "V"})
    
    return()

# Tutorial_7 produces a thermal model for the Li_ion simulation
def Tutorial_7():
    options = {"thermal": 'x-full'}
    
    model = bam.lithium_ion.SPMe(options=options)
    
    parameter_values = model.default_parameter_values
    parameter_values["Current function [A]"] = 3
    
    sim = bam.Simulation(model, parameter_values=parameter_values)
    sim.solve([0, 3600])
    
    sim.plot(['Cell temperature [K]', 'Total heating [W.m-3]', 'Current [A]',
              'Terminal voltage [V]'])
    
    return()

# Tutorial_8 shows two different solves and allows us to see the differences in 
# solve times.
def Tutorial_8():
    model = bam.lithium_ion.DFN()
    param = model.default_parameter_values
    param['Lower voltage cut-off [V]'] = 3.6
    
    safe_solver = bam.CasadiSolver(atol=1e-3, rtol=1e-3, mode='safe')
    fast_solver = bam.CasadiSolver(atol=1e-3, rtol=1e-3, mode='fast')
    
    safe_sim = bam.Simulation(model, parameter_values=param, solver = safe_solver)
    fast_sim = bam.Simulation(model, parameter_values=param, solver = fast_solver)
    
    safe_sim.solve([0, 3600])
    print("Safe mode solve time: {}".format(safe_sim.solution.solve_time))
    fast_sim.solve([0, 3600])
    print("Fast mode solve time: {}".format(fast_sim.solution.solve_time))

    bam.dynamic_plot([safe_sim, fast_sim])
    
    return()


def Tutorial_9():
    model = bam.lithium_ion.SPMe()
    model.default_var_pts
    
    var = bam.standard_spatial_vars
    
    # Dictionary
    var_pts = {
        var.x_n: 10, # negative electrode
        var.x_s: 10, # seperator
        var.x_p: 10, # positive electrode
        var.r_n: 10, # negative particle
        var.r_p: 10, # positive particle
        }
    
    sim = bam.Simulation(model, var_pts=var_pts)
    sim.solve([0, 3600])
    sim.plot()
    
    # Mesh refinement study
    npts = [4, 8, 16, 32, 64]
    
    model = bam.lithium_ion.DFN()
    chemistry = bam.parameter_sets.Ecker2015
    parameter_values = bam.ParameterValues(chemistry=chemistry)
    
    solver = bam.CasadiSolver(mode='fast')
    
    solutions = []
    for N in npts:
        var_pts = {
            var.x_n: N, # negative electrode
            var.x_s: N, # seperator
            var.x_p: N, # positive electrode
            var.r_n: N, # negative particle
            var.r_p: N, # positive particle
        }
    
        sim = bam.Simulation(
        model, solver=solver, parameter_values=parameter_values, var_pts=var_pts
    )
    sim.solve([0, 3600])
    solutions.append(sim.solution)
    
    bam.dynamic_plot(solutions, ["Terminal voltage [V]"], time_unit="seconds", labels=npts)
    
    return()

if __name__ == '__main__':
    # Tutorial_1()
    # Tutorial_2()
    # Tutorial_3()
    # Tutorial_4()
    # Tutorial_5()
    # Tutorial_6()
     Tutorial_7()
    # Tutorial_8()
    # Tutorial_9()
