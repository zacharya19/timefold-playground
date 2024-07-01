from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from typing import Annotated

from .domain import *
from .score_analysis import *
from .constraints import define_constraints
from .demo_data import DemoData, generate_demo_data
from .solver import solver_manager, solution_manager


app = FastAPI(docs_url='/q/swagger-ui')
data_sets: dict[str, TechnicianRoutePlan] = {}


@app.get("/demo-data")
async def demo_data_list():
    return [e.name for e in DemoData]


@app.get("/demo-data/{dataset_id}", response_model_exclude_none=True)
async def get_demo_data(dataset_id: str) -> TechnicianRoutePlan:
    demo_data = generate_demo_data(getattr(DemoData, dataset_id))
    return demo_data


@app.get("/route-plans/{problem_id}", response_model_exclude_none=True)
async def get_route(problem_id: str) -> TechnicianRoutePlan:
    route = data_sets[problem_id]
    return route.model_copy(update={
        'solver_status': solver_manager.get_solver_status(problem_id),
    })


def update_route(problem_id: str, route: TechnicianRoutePlan):
    global data_sets
    data_sets[problem_id] = route


def json_to_technician_route_plan(json: dict) -> TechnicianRoutePlan:
    visits = {
        visit['id']: visit for visit in json.get('visits', [])
    }
    technicians = {
        technician['id']: technician for technician in json.get('technicians', [])
    }

    for visit in visits.values():
        if 'technician' in visit:
            del visit['technician']

        if 'previousVisit' in visit:
            del visit['previousVisit']

        if 'nextVisit' in visit:
            del visit['nextVisit']

    visits = {visit_id: Visit.model_validate(visits[visit_id]) for visit_id in visits}
    json['visits'] = list(visits.values())

    for technician in technicians.values():
        technician['visits'] = [visits[visit_id] for visit_id in technician['visits']]

    json['technicians'] = list(technicians.values())

    return TechnicianRoutePlan.model_validate(json, context={
        'visits': visits,
        'technicians': technicians
    })


async def setup_context(request: Request) -> TechnicianRoutePlan:
    json = await request.json()
    return json_to_technician_route_plan(json)


@app.post("/route-plans")
async def solve_route(route: Annotated[TechnicianRoutePlan, Depends(setup_context)]) -> str:
    data_sets['ID'] = route
    solver_manager.solve_and_listen('ID', route,
                                    lambda solution: update_route('ID', solution))
    return 'ID'


@app.put("/route-plans/analyze")
async def analyze_route(route: Annotated[TechnicianRoutePlan, Depends(setup_context)]) \
        -> dict['str', list[ConstraintAnalysisDTO]]:
    return {'constraints': [ConstraintAnalysisDTO(
        name=constraint.constraint_name,
        weight=constraint.weight,
        score=constraint.score,
        matches=[
            MatchAnalysisDTO(
                name=match.constraint_ref.constraint_name,
                score=match.score,
                justification=match.justification
            )
            for match in constraint.matches
        ]
    ) for constraint in solution_manager.analyze(route).constraint_analyses]}


@app.delete("/route-plans/{problem_id}")
async def stop_solving(problem_id: str) -> None:
    solver_manager.terminate_early(problem_id)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
