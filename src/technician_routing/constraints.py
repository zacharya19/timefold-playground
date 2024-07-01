from timefold.solver.score import ConstraintFactory, HardSoftScore, constraint_provider

from .domain import *
from .score_analysis import *

TECHNICIAN_CAPACITY = "technicianCapacity"
TECHNICIAN_MUST_WORK = "technicianMustWork"
MINIMIZE_TRAVEL_TIME = "minimizeTravelTime"


@constraint_provider
def define_constraints(factory: ConstraintFactory):
    return [
        # Hard constraints
        technician_capacity(factory),
        # Soft constraints
        minimize_travel_time(factory)
    ]

##############################################
# Hard constraints
##############################################


def technician_capacity(factory: ConstraintFactory):
    return (factory.for_each(Technician)
            .filter(lambda technician: technician.calculate_total_demand() > technician.capacity)
            .penalize(HardSoftScore.ONE_HARD,
                      lambda technician: technician.calculate_total_demand() - technician.capacity)
            .justify_with(lambda technician, score:
                          TechnicianCapacityJustification(
                              technician.id,
                              technician.capacity,
                              technician.calculate_total_demand()))
            .as_constraint(TECHNICIAN_CAPACITY)
            )

def technician_not_working(factory: ConstraintFactory):
    return (factory.for_each(Technician).filter(lambda technician: len(technician.visits) < 10)
                .penalize(HardSoftScore.ONE_HARD, lambda technician: 1)
                .justify_with(lambda technician, score:
                          TechnicianAssignmentConstraintProvider(
                              technician.id))
            .as_constraint(TECHNICIAN_MUST_WORK))
##############################################
# Soft constraints
##############################################


def minimize_travel_time(factory: ConstraintFactory):
    return (
        factory.for_each(Technician)
        .penalize(HardSoftScore.ONE_SOFT,
                  lambda technician: technician.calculate_total_driving_time_seconds())
        .justify_with(lambda technician, score:
                      MinimizeTravelTimeJustification(
                          technician.id,
                          technician.calculate_total_driving_time_seconds()))
        .as_constraint(MINIMIZE_TRAVEL_TIME)
    )
