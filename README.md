# INF Tool — National Influence in Clause Dissemination across BITs

An interactive [Dash](https://dash.plotly.com/) dashboard that estimates each
country's **influence ("INF weight")** in the dissemination of
health-safeguarding clauses across **bilateral investment treaties (BITs)**,
using NLP-based text similarity between treaty clauses.

This repository is the reference implementation accompanying the peer-reviewed
study below, and serves as a worked example of turning a research method into a
deployable, interactive tool.

> Uddin, S., Lu, H., Alschner, W., Patay, D., Frank, N., Gomes, F.S., & Thow, A.M. (2024).
> *An NLP-based novel approach for assessing national influence in clause dissemination across bilateral investment treaties.*
> **PLOS ONE, 19(3): e0298380.**
> https://doi.org/10.1371/journal.pone.0298380

---

## What it does

Treaties borrow language from one another. By measuring the textual similarity
between health-related clauses across thousands of BITs, the tool quantifies
which countries act as **originators / diffusers** of particular clause
strategies. Users can:

- Choose a **clause strategy** — *Defensive*, *Neutral*, or *Progressive*.
- Constrain the analysis to a **similarity range** and a **year range**.
- See the country that **plays the major role** and a full **ranking of
  countries by INF weight**.

### How the INF weight is computed

1. Filter the similar-clause pairs for the chosen strategy to the selected
   similarity range.
2. Restrict BITs to the selected signature-year range.
3. Count how often each BIT appears across the filtered similar pairs and
   normalise these counts into weights (each weight is a share of the total).
4. Attribute each BIT's weight to **both** of its signatory countries and sum
   per country to obtain the final ranking.

---

## Project structure

```
.
├── app.py             # Dash application (layout, computation, callbacks)
├── data/              # Input datasets
│   ├── bit.csv        # BIT metadata (id, signatory countries, year, ...)
│   ├── defensive.xlsx # Similar clause pairs — defensive strategy
│   ├── neutral.xlsx   # Similar clause pairs — neutral strategy
│   └── offensive.xlsx # Similar clause pairs — progressive strategy
├── assets/
│   └── logo.png       # Header logo (auto-served by Dash from /assets)
├── requirements.txt   # Python dependencies
├── Procfile           # Process definition for gunicorn-based hosts
├── runtime.txt        # Pinned Python version for the host
└── LICENSE
```

---

## Getting started

### Prerequisites

- Python 3.9+ (3.11 recommended)

### Installation

```bash
git clone https://github.com/haohuilu/inf.git
cd inf

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Run locally

```bash
python app.py
```

Then open http://127.0.0.1:8050 in your browser.

The host, port, and debug mode can be overridden with environment variables:

```bash
HOST=0.0.0.0 PORT=8050 DEBUG=true python app.py
```

---

## Deployment

The app exposes a WSGI server object (`server = app.server`), so it runs on any
gunicorn-compatible host (Render, Heroku, Railway, etc.):

```bash
gunicorn app:server
```

The included `Procfile` and `runtime.txt` configure this automatically on
platforms that support them.

---

## Data

| File | Sheet | Key columns |
| --- | --- | --- |
| `data/bit.csv` | — | `BIT_ID`, `Country 1`, `Country 2`, `Year` (plus clause-classification fields) |
| `data/defensive.xlsx` | `similar_pairs_defensive_all` | `BIT1`, `BIT2`, `similarity` |
| `data/neutral.xlsx` | `similar_pairs_neutral_all` | `BIT1`, `BIT2`, `similarity` |
| `data/offensive.xlsx` | `similar_pair_offensive_all` | `BIT1`, `BIT2`, `similarity` |

The `similarity` column holds the pairwise text-similarity score (0–1) between
two BITs' clauses for the given strategy.

---

## Citation

If you use this tool in your research, please cite:

```bibtex
@article{uddin2024inf,
  title   = {An NLP-based novel approach for assessing national influence in clause dissemination across bilateral investment treaties},
  author  = {Uddin, Shahadat and Lu, Haohui and Alschner, Wolfgang and Patay, Dori and Frank, Nicholas and Gomes, Fabio S. and Thow, Anne Marie},
  journal = {PLOS ONE},
  volume  = {19},
  number  = {3},
  pages   = {e0298380},
  year    = {2024},
  doi     = {10.1371/journal.pone.0298380}
}
```

## License

Released under the [MIT License](LICENSE). © 2023 The University of Sydney.
