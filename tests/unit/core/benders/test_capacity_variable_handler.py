

# test_capacity_variable_handler.py
import pytest
import pandas as pd
from pyomo.environ import (
    ConcreteModel, Var, Constraint, Param, Objective, SolverFactory, minimize, value
)
from pyomo.opt import TerminationCondition
from capacity_variable_handler import CapacityVariableHandler  # your class


@pytest.fixture
def simple_subproblem():
    """
    Build a tiny LP:
        min x
        s.t.  y - 2x <= 4
              y >= 0, x >= 0
    """
    m = ConcreteModel()
    m.x = Var(bounds=(0, None))
    m.y = Var(bounds=(0, None))

    # constraint: y - 2x <= 4
    m.cons = Constraint(expr=m.y - 2 * m.x <= 4)

    m.obj = Objective(expr=m.x, sense=minimize)

    # attach duals
    m.dual = SolverFactory("glpk").solve(m, tee=False).solve_suffixes = ["dual"]

    return m


def test_extract_duals_no_coeff(simple_subproblem):
    m = simple_subproblem

    # handler with no coefficient
    handler = CapacityVariableHandler(
        constraint_name="cons",
        constraint_indices=[()],
        constraint_index_names=["idx"],
        capacity_var_name="x",
        capacity_var_index_selection_func=lambda idx: (),  # no index here
        has_coefficient=False,
        index_names_to_keep=["idx"],
    )

    handler.extract_duals(m)
    assert isinstance(handler.duals, pd.Series)
    assert handler.duals.index.names == ["idx"]

    handler.extract_coefficients(m)
    assert all(handler.coefficients == 1.0)

    result = handler.extract_data(m)
    assert isinstance(result, pd.Series)
    # should equal dual * 1
    pd.testing.assert_series_equal(result, handler.duals.groupby("idx").sum())


def test_extract_duals_with_coeff():
    """
    Same idea, but with a parameter coefficient.
    """
    m = ConcreteModel()
    m.x = Var(bounds=(0, None))
    m.y = Var(bounds=(0, None))
    m.coeff = Param(initialize=2)

    m.cons = Constraint(expr=m.y - m.coeff * m.x <= 4)
    m.obj = Objective(expr=m.x, sense=minimize)

    opt = SolverFactory("glpk")
    res = opt.solve(m, tee=False, suffixes=["dual"])
    assert res.solver.termination_condition == TerminationCondition.optimal

    handler = CapacityVariableHandler(
        constraint_name="cons",
        constraint_indices=[()],
        constraint_index_names=["idx"],
        capacity_var_name="x",
        capacity_var_index_selection_func=lambda idx: (),
        has_coefficient=True,
        coefficients_subproblem_name="coeff",
        coefficient_index_selection_func=lambda idx: (),  # same index
        index_names_to_keep=["idx"],
    )

    result = handler.extract_data(m)
    # should be dual * coeff
    expected = handler.duals * handler.coefficients
    pd.testing.assert_series_equal(result, expected.groupby("idx").sum())