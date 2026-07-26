# Outputs

Generated artifacts. Everything here is reproducible from `analysis/` — nothing is
hand-made, and nothing here should be edited directly.

```
figures/   results figures used in the thesis
tables/    exported result tables
```

Regenerate with:

```bash
python analysis/scripts/make_results_figures.py
```

The generator is self-verifying: it recomputes every plotted statistic and prints
PASS/FAIL against the values reported in the thesis, so a figure cannot silently drift
from the text. Re-run it after any change to the data or the analysis.
