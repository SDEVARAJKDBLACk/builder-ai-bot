import pandas as pd
from datetime import datetime

def export_excel(data):
    df = pd.DataFrame(data)
    name = f"ai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(name,index=False)
