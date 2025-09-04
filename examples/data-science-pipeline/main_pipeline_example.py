# examples/data-science-pipeline/main_pipeline_example.py
import pandas as pd
from fastapi import FastAPI
from typing import List, Set, Dict, Any

# --- שלב 1: ייבוא הרכיבים הניתנים לשימוש חוזר מהספרייה ---
# נניח שהעתקנו את הקבצים האלה לפרויקט שלנו
from configuration_templates.data_science.data_loader import DataHandler
from configuration_templates.data_science.text_feature_processor import TextFeatureProcessor


# --- שלב 2: הגדרת ה-Pipeline ---
class AnalysisPipeline:
    def __init__(self, file_path: str, text_column: str):
        self.file_path = file_path
        self.text_column = text_column
        self.data_handler = DataHandler(file_path)
        self.feature_processor = TextFeatureProcessor()
        self.processed_df = pd.DataFrame()

    def run(self, keywords_to_find: Set[str] = None):
        """Executes the full ETL process."""
        # 1. Extract: Load data
        raw_df = self.data_handler.load_data()

        # 2. Transform: Apply all text features
        self.processed_df = self.feature_processor.apply_all_features(
            df=raw_df,
            text_column=self.text_column,
            keyword_set=keywords_to_find
        )

        # 3. Prepare for Load/Serve: Final cleanup
        # (לדוגמה: בחירת עמודות, שינוי שמות)
        self.processed_df = self.processed_df.rename(columns={"_id": "id"})
        # ... התאמות נוספות לפי הצורך ...

    def get_results(self) -> List[Dict[str, Any]]:
        """Returns the final processed data as a list of dictionaries."""
        return self.processed_df.to_dict(orient='records')


# --- שלב 3: שילוב ב-FastAPI ---

# נתונים גלובליים שיותחלו בעליית השרת
processed_data_cache: List[Dict[str, Any]] = []

app = FastAPI(
    title="Data Science Pipeline Example",
    on_startup=[
        lambda: (
            pipeline := AnalysisPipeline(file_path="path/to/your/data.csv", text_column="tweet_text"),
            pipeline.run(keywords_to_find={"danger", "secret"}),
            processed_data_cache.extend(pipeline.get_results())
        )
    ]
)


@app.get("/processed-data")
def get_processed_data() -> List[Dict[str, Any]]:
    """Endpoint to serve the pre-processed data."""
    return processed_data_cache

# להרצה מקומית: uvicorn main_pipeline_example:app --reload