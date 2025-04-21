from pathlib import Path
import pandas as pd



app_dir = Path(__file__).parent



tips = pd.read_csv(app_dir/"tips.csv")

bill_rng = (min(tips.total_bill), max(tips.total_bill))
