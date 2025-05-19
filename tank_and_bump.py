import Fuzzy_Regulator as FR
import fuzzylab as fl

#Ёмкость.
tank = FR.FuzzyRegulator()
parameters = [
    [-1, 0.4],
    [0, 0.4],
    [1, 0.4]
]
tank.add_input('dH', "NO-PO", parameters)
tank.add_input('dU', 'NO-PO', parameters)
parameters = [
    [-2, -1, -0.5],
    [-1, -0.5, 0],
    [-0.5, 0, 0.5],
    [0, 0.5, 1],
    [0.5, 1, 2]
]
tank.add_output('CommandToValve', 'Z-O', parameters)
rule_list=[
    [3, 0, 1, 2, 1],
    [2, 3, 2, 1, 1],
    [2, 0, 3, 1, 1],
    [2, 1, 4, 1, 1],
    [1, 0, 5, 2, 1]
]
tank.add_rules(rule_list)

#Насос.
bump = FR.FuzzyRegulator()
parameters = [
    [0.4, -1],
    [0.4, 0],
    [0.4, 1]
]
bump.add_input('input_1', 'NO-PO', parameters)
bump.add_input('input_2', 'NO-PO', parameters)
fl.plotmf(bump, 'input', 1)
fl.plotmf(bump, 'input', 2)
parameters = [
    [-1, 0, 0.25],
    [0, 0.25, 0.5],
    [0.25, 0.5, 0.75],
    [0.5, 0.75, 1],
    [0.75, 1, 2]
]
bump.add_output('pow', 'Z-O', parameters)
rule_list=[
    [3, 0, 1, 2, 1],
    [2, 3, 2, 1, 1],
    [2, 0, 3, 1, 1],
    [2, 1, 4, 1, 1],
    [1, 0, 5, 2, 1]
]
tank.add_rules(rule_list)