# BIM Benchmark Answer Scripts

I built this toolkit during my internship with the Generative Design team at the Artificial Intelligence Research Institute (AIRI) in Moscow, Russia. The GitLab remote keeps the internal branch, this GitHub fork is the public-friendly snapshot. Some of the proprietary features I worked on are still under NDA so they are not shown here.

## What’s in the repo

- `src/bim_benchmark/` - small Python package with the CLI, the path helpers and the multiprocessing runner.
- `scripts/` - the per-question scripts (Q001-Q110).
- `data/questions.csv` - the catalogue of questions and paths to the script that answers them.
- `data/reference_models/` - open-source IFC models. They are much simpler than the internal AIRI models, so a lot of questions return `0`, empty strings or placeholders.
- `data/benchmark_results/` - CSV outputs produced from the models.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_all_models.py  # run every model
python run_all_models.py data/reference_models/SimpleWall.ifc --question-id Q001
python -m bim_benchmark.cli data/reference_models  # same run via the CLI module
```

Use repeated `--question-id` flags to limit the run while you debug individual scripts.

## Question catalogue (sample)

| question_id | question_text                                             | description                                       | difficulty | script_path                     |
| ----------- | --------------------------------------------------------- | ------------------------------------------------- | ---------- | ------------------------------- |
| Q001        | How many walls are there in the building?                 | Counts every wall element in the IFC model.       | easy       | scripts/001_count_walls.py      |
| Q002        | How many doors are there in the building?                 | Counts every door element in the IFC model.       | easy       | scripts/002_count_doors.py      |
| Q003        | What are the names of all floors/storeys in the building? | Lists the storey names defined for the building.  | easy       | scripts/003_list_storeys.py     |
| Q004        | What is the total floor area of all spaces?               | Sums the floor area of every space in the model.  | medium     | scripts/004_total_floor_area.py |
| Q005        | What is the overall building height?                      | Calculates the height from the storey elevations. | medium     | scripts/005_building_height.py  |

## Benchmark results (open-source models only)

Because I can only publish open-source IFC files, the example outputs are very sparse - many elements simply don’t exist in these models. The production datasets at AIRI are much richer, but I’m not allowed to share them yet.

`data/benchmark_results/SimpleWall_answers.csv`:

```csv
question_id,question,result,difficulty,model,time_seconds
Q001,How many walls are there in the building?,1,easy,data/reference_models/SimpleWall.ifc,2.983
```

`data/benchmark_results/AdvancedProject_answers.csv` (trimmed):

```csv
question_id,question,result,difficulty
Q001,How many walls are there in the building?,0,easy
Q004,What is the total floor area of all spaces?,0.0,medium
Q015,Which floor has the most rooms?,,medium
Q038,How many windows are there on each storey?,,medium
Q066,What are the top 10 largest spaces by area?,,medium
```

Empty rows in the second snippet show where the public model lacks the metadata needed to answer a question.

## Screenshot reference

![AdvancedProject overview](docs/images/advanced-project-overview.png)

Screenshot of one of the more complex models.

## Notes

- Results end up in `data/benchmark_results/<model>_answers.csv`. GitLab remote ignores (`.gitignore`) them because the benchmarks results should be stored separately in an internal server.
- Push to GitLab with plain `git push`. Use `git pushgh <branch>` when you need to sync this fork.
