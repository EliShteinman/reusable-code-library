# configuration-templates/data-science/etl_manager_template.py
import logging
import pandas as pd
from typing import List, Dict, Any, Set

# TODO: Import your specific processor
from .text_feature_processor import TextFeatureProcessor

logger = logging.getLogger(__name__)


class ETLManager:
    """
    Manages the ETL (Extract, Transform, Load) pipeline:
    1. Takes raw data (Extract).
    2. Uses a processor to enrich it (Transform).
    3. Prepares the final data for serving (Load/Serve).
    """

    def __init__(self, raw_data: List[Dict[str, Any]]):
        logger.info(f"Initializing ETLManager with {len(raw_data)} raw records.")
        self.raw_data = raw_data
        self.df = pd.DataFrame()

        # TODO: Instantiate your chosen processor
        self.processor = TextFeatureProcessor()

        # TODO: Define path to any required resource files
        self.keyword_file_path = "data/keywords.txt"

    def _load_resources(self) -> Set[str]:
        """Template for loading external resources like keyword lists."""
        try:
            with open(self.keyword_file_path, "r", encoding="utf-8") as f:
                keywords = {line.strip() for line in f if line.strip()}
            logger.info(f"Loaded {len(keywords)} keywords from {self.keyword_file_path}")
            return keywords
        except FileNotFoundError:
            logger.warning(
                f"Keyword file not found at: {self.keyword_file_path}. Proceeding without keyword detection.")
            return set()

    def _finalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares the DataFrame for the final output.
        - Renames columns to match API specification.
        - Fills null values.
        - Selects and orders the final columns.
        """
        # TODO: Customize column renaming map
        rename_map = {
            "_id": "id",
            "Text": "original_text"
        }
        df = df.rename(columns=rename_map)

        # TODO: Fill NaN values as required by the output format
        if 'keywords_detected' in df.columns:
            df['keywords_detected'] = df['keywords_detected'].fillna("")

        # TODO: Define the exact columns and order for the final output
        final_columns = ["id", "original_text", "rarest_word", "sentiment", "keywords_detected"]

        # Filter to keep only the required columns
        existing_final_columns = [col for col in final_columns if col in df.columns]
        return df[existing_final_columns]

    def run_pipeline(self):
        """Executes the full ETL pipeline."""
        logger.info("Starting ETL pipeline...")
        if not self.raw_data:
            logger.warning("Raw data is empty. Pipeline finished.")
            return

        try:
            # 1. Convert to DataFrame
            self.df = pd.DataFrame(self.raw_data)
            logger.info(f"Converted raw data to DataFrame with {self.df.shape[0]} rows and {self.df.shape[1]} columns.")

            # 2. Load external resources (e.g., keywords)
            keywords = self._load_resources()

            # 3. Process data to generate features
            # TODO: Specify the name of the text column from your source data
            text_column_name = "Text"
            self.df = self.processor.apply_all_features(self.df, text_column_name, keywords)
            logger.info("Feature engineering complete.")

            # 4. Finalize the DataFrame for output
            self.df = self._finalize_dataframe(self.df)
            logger.info("DataFrame finalized for API output.")

        except Exception as e:
            logger.error(f"An error occurred during the ETL pipeline: {e}", exc_info=True)
            # Ensure we have an empty DataFrame in case of failure
            self.df = pd.DataFrame()

    def get_processed_data_as_dicts(self) -> List[Dict[str, Any]]:
        """Returns the processed data in the required list of dictionaries format."""
        if self.df.empty:
            logger.warning("Processed data is empty.")
            return []

        return self.df.to_dict(orient="records")