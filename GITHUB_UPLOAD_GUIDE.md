# GitHub upload checklist

## Upload this exact repository structure

Upload the **contents of this folder** to the root of your GitHub repository named `FactoryMind`.

```text
README.md
GITHUB_UPLOAD_GUIDE.md
LICENSE
.gitignore
requirements.txt
pyproject.toml
app.py

src/
  __init__.py
  p2_integration.py
  p4_integration.py
  decarbonization.py

data/
  FactoryMind_P2_Final_ys.csv
  FactoryMind_Feature_Engineering.csv

validation/
  validate_factorymind.py

docs/
  README.md
  DEMO_RUNBOOK.md
  P2_Final_Validation.md
  P4_Operational_Stress_Test.md

screenshots/
  README.md
  dashboard.png
  decision.png
  whatif.png
  decarbonization.png

presentation/
  FactoryMind_Final_Submission_12Slides_FINAL.pptx
  FactoryMind_Final_Submission_12Slides_FINAL.pdf

.github/workflows/
  validate.yml
```

## Do not upload

Do **not** upload `__pycache__/`, `.pyc` files, virtual-environment folders, editor folders, or temporary files. The repository `.gitignore` already excludes them.

Do not add older duplicate `app(1).py`, `app(2).py`, `app(3).py`, `p2_integration(1).py`, or `p4_integration(1).py` snapshots. The packaged files here are the cleaned paths to use.

The older `FactoryMind_Decarbonization_Demo.csv` snapshot is intentionally not included in this final repo because it contains an earlier illustrative state that does not match the frozen Case 4 / Run 6 values in the current dashboard. The live prototype derives its decarbonisation scenario from the feature-engineering dataset and explicit assumptions.

## Easiest Git workflow

From this folder:

```bash
git init
git add .
git commit -m "FactoryMind final hackathon submission"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

## Streamlit deployment

For Streamlit Community Cloud, point the app to:

```text
app.py
```

The repository root should remain the working directory so the app can locate `src/` and `data/`.
