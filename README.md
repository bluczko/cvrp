# CVRP Project
Practical implementation of Constrained Vehicle Routing Problem.

This is a students project for Systems Engineering course.

## Installation

Python 3.7 or newer is required. This project is OS-agnostic.

Install required pip packages:
```
pip install -r requirements.txt
```

## Solvers
Additionally, this project requires installation of any MLP solver supported by Pyomo. 

GLPS was used in testing, but Gurobi or CPLEX is recommended for performance reasons.

Full list of supported solvers is available from pyomo command (after installation):
```
pyomo help --solvers
```
