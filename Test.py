import pybamm

model = pybamm.lithium_ion.SPMe()

chemistry = pybamm.parameter_sets.NCA_Kim2011

parameter_value = pybamm.ParameterValues(chemistry = chemistry)

print(model.variable_names())