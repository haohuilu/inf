"""INF Tool — National influence in clause dissemination across BITs.

An interactive Dash dashboard that estimates each country's influence ("INF
weight") in the dissemination of health-safeguarding clauses across bilateral
investment treaties (BITs), based on text-similarity between treaty clauses.

The methodology is described in:

    Uddin, S., Lu, H., Alschner, W., Patay, D., Frank, N., Gomes, F.S., &
    Thow, A.M. (2024). An NLP-based novel approach for assessing national
    influence in clause dissemination across bilateral investment treaties.
    PLOS ONE, 19(3): e0298380.
    https://doi.org/10.1371/journal.pone.0298380

Run locally:
    python app.py

Run in production (e.g. on Render/Heroku):
    gunicorn app:server
"""

import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html
from dash.dash_table.Format import Format

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
DATA_DIR = Path(__file__).parent / "data"

# Each strategy maps to its source workbook and the sheet holding the
# similar-clause pairs for that strategy.
STRATEGY_SOURCES = {
    "defensive": ("defensive.xlsx", "similar_pairs_defensive_all"),
    "neutral": ("neutral.xlsx", "similar_pairs_neutral_all"),
    "offensive": ("offensive.xlsx", "similar_pair_offensive_all"),
}

# Defaults for the input controls.
DEFAULT_SIMILARITY = (0.0, 1.0)
DEFAULT_YEAR_RANGE = (1959, 2022)

CITATION_DOI = "https://doi.org/10.1371/journal.pone.0298380"

# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def load_similarity_data():
    """Load the similar-clause pairs for every strategy into a dict of frames."""
    return {
        strategy: pd.read_excel(DATA_DIR / filename, sheet_name=sheet)
        for strategy, (filename, sheet) in STRATEGY_SOURCES.items()
    }


def load_bit_metadata():
    """Load BIT metadata, keeping only the columns the dashboard needs."""
    bit = pd.read_csv(DATA_DIR / "bit.csv")
    return bit[["BIT_ID", "Country 1", "Country 2", "Year"]]


similarity_by_strategy = load_similarity_data()
bit_metadata = load_bit_metadata()

# --------------------------------------------------------------------------- #
# Core computation
# --------------------------------------------------------------------------- #
def compute_country_weights(strategy, sim_start, sim_end, year_start, year_end):
    """Return a frame of countries ranked by their INF weight.

    The weight of a country is the share of similar-clause pairs (within the
    selected similarity and year range) in which one of its BITs appears.
    """
    pairs = similarity_by_strategy[strategy]
    pairs = pairs[(pairs["similarity"] >= sim_start) & (pairs["similarity"] <= sim_end)]

    bits = bit_metadata[
        (bit_metadata["Year"] >= year_start) & (bit_metadata["Year"] <= year_end)
    ]

    # Frequency with which each BIT appears across the filtered similar pairs.
    freq = (
        pd.concat([pairs["BIT1"], pairs["BIT2"]])
        .value_counts()
        .reset_index()
    )
    freq.columns = ["BIT_ID", "Frequency"]
    if freq.empty:
        return pd.DataFrame(columns=["Country", "Weight"])

    freq["Weight"] = freq["Frequency"] / freq["Frequency"].sum()

    # Attribute each BIT's weight to both of its signatory countries.
    merged = pd.merge(freq, bits, on="BIT_ID", how="inner")
    country_weight = pd.concat(
        [
            merged[["Country 1", "Weight"]],
            merged[["Country 2", "Weight"]].rename(columns={"Country 2": "Country 1"}),
        ]
    )

    weights = (
        country_weight.groupby("Country 1")["Weight"]
        .sum()
        .reset_index()
        .sort_values(by="Weight", ascending=False)
        .rename(columns={"Country 1": "Country"})
    )
    weights["Weight"] = weights["Weight"].round(4)
    return weights


# --------------------------------------------------------------------------- #
# App & layout
# --------------------------------------------------------------------------- #
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="INF Tool — National influence across BITs",
)
server = app.server  # WSGI entry point for gunicorn

CITATION = html.P(
    [
        "Uddin, S., Lu, H., Alschner, W., Patay, D., Frank, N., Gomes, F.S., and Thow, A.M., ",
        html.I(
            "An NLP-based novel approach for assessing national influence in "
            "clause dissemination across bilateral investment treaties"
        ),
        ". PLOS ONE, ",
        html.B("19"),
        "(3): e0298380. ",
        html.A(CITATION_DOI, href=CITATION_DOI, target="_blank"),
    ],
    style={"marginBottom": "20px", "fontSize": "14px"},
)

controls = html.Div(
    [
        html.Div(
            [
                html.P(
                    [
                        "Demo Video: ",
                        html.Br(),
                        html.A("http://video.inftool.com", href="http://video.inftool.com", target="_blank"),
                        html.Br(),
                        "Chatbot (beta): ",
                        html.A("http://chatbot.inftool.com", href="https://chatbot.inftool.com", target="_blank"),
                        html.Br(),
                        "Text Similarity Tool: ",
                        html.Br(),
                        html.A("https://bitsimilarity.onrender.com", href="https://bitsimilarity.onrender.com", target="_blank"),
                    ],
                    style={"marginBottom": "20px", "fontSize": "14px"},
                )
            ],
            style={"padding": "10px 0"},
        ),
        dcc.RadioItems(
            options=[
                {"label": " Defensive", "value": "defensive"},
                {"label": " Neutral", "value": "neutral"},
                {"label": " Progressive", "value": "offensive"},
            ],
            value="defensive",
            id="strategy-selection",
            style={"marginBottom": "20px"},
        ),
        html.Div(
            [
                html.Label("Similarity Range:"),
                dcc.Input(
                    id="similarity-start-input", type="number",
                    value=DEFAULT_SIMILARITY[0], step=0.01, style={"marginRight": "10px"},
                ),
                dcc.Input(
                    id="similarity-end-input", type="number",
                    value=DEFAULT_SIMILARITY[1], step=0.01,
                ),
            ],
            style={"marginTop": "10px"},
        ),
        html.Div(
            [
                html.Label("Year Range:", style={"marginTop": "20px"}),
                dcc.Input(
                    id="year-start-input", type="number",
                    value=DEFAULT_YEAR_RANGE[0], style={"marginRight": "10px"},
                ),
                dcc.Input(
                    id="year-end-input", type="number", value=DEFAULT_YEAR_RANGE[1],
                ),
            ],
            style={"marginTop": "10px"},
        ),
        html.Div(
            [dbc.Button("Calculate", id="calculate-button", color="primary", className="mt-2")],
            style={"marginTop": "20px"},
        ),
        html.Div(
            [
                html.P(
                    "Researchers using this tool for research should cite the following article:",
                    style={"fontStyle": "italic"},
                ),
                CITATION,
            ],
            style={"padding": "10px 0"},
        ),
    ],
    style={"width": "25%", "padding": "20px", "borderRight": "solid 1px #ddd"},
)

results = html.Div(
    [
        html.Div(
            id="major-role-card",
            className="card",
            style={
                "margin": "20px", "padding": "20px", "border": "1px solid #ddd",
                "borderRadius": "5px", "background": "#f9f9f9",
            },
        ),
        html.Div(id="output-table", style={"margin": "20px"}),
    ],
    style={"width": "75%", "padding": "20px"},
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(src="/assets/logo.png", id="logo", style={"height": "80px"}),
                        html.H2(
                            "National influence in clause dissemination for "
                            "safeguarding health across BITs",
                            style={"marginLeft": "20px"},
                        ),
                    ],
                    style={
                        "display": "flex", "alignItems": "center", "background": "#f4f4f4",
                        "borderBottom": "solid 1px #ddd", "padding": "10px",
                    },
                ),
                html.Div(
                    [controls, results],
                    style={"display": "flex", "flexDirection": "row"},
                ),
            ],
            style={"maxWidth": "1200px", "margin": "0 auto"},
        ),
        html.Div(
            [
                html.P(
                    "© 2023 The University of Sydney",
                    style={"textAlign": "center", "margin": "20px", "fontSize": "12px", "color": "#999"},
                )
            ],
            style={"borderTop": "1px solid #ddd", "background": "#f4f4f4"},
        ),
    ]
)


# --------------------------------------------------------------------------- #
# Callbacks
# --------------------------------------------------------------------------- #
@app.callback(
    [Output("output-table", "children"), Output("major-role-card", "children")],
    [Input("calculate-button", "n_clicks")],
    [
        State("similarity-start-input", "value"),
        State("similarity-end-input", "value"),
        State("year-start-input", "value"),
        State("year-end-input", "value"),
        State("strategy-selection", "value"),
    ],
)
def update_table(n_clicks, sim_start, sim_end, year_start, year_end, strategy):
    """Recompute the ranking table and the "major role" card on demand."""
    weights = compute_country_weights(strategy, sim_start, sim_end, year_start, year_end)

    if weights.empty:
        card = [html.H4("No Info Available")]
        table = html.Div(["No information available for the selected year(s)."])
        return table, card

    top = weights.iloc[0]
    card = [
        html.H4("Who plays the major role?"),
        html.H2(top["Country"]),
        html.P(f"Weight: {top['Weight']:.4f}"),
    ]

    table = dash_table.DataTable(
        columns=[
            {"name": "Country", "id": "Country"},
            {"name": "INF Weight", "id": "Weight", "type": "numeric", "format": Format(precision=4)},
        ],
        data=weights.to_dict("records"),
        page_size=100,
        style_table={"height": "400px", "overflowY": "auto"},
        style_header={
            "fontWeight": "bold", "color": "black",
            "border": "1px solid black", "textAlign": "center",
        },
        style_cell={"textAlign": "center"},
    )
    return table, card


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", 8050)),
        debug=os.environ.get("DEBUG", "false").lower() == "true",
    )
