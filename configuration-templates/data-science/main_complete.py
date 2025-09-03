# configuration-templates/data-science/main_complete.py
"""
Complete Twitter Sentiment Analysis Pipeline
Based on the exam requirements with proper OOP structure and error handling.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Import our custom classes
from data_loader import DataHandler
from text_data_cleaner import TextDataCleaner
from text_data_analyzer import TextDataAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('analysis.log')
    ]
)
logger = logging.getLogger(__name__)


class TwitterAnalysisPipeline:
    """
    Complete pipeline for Twitter antisemitism analysis.
    Handles data loading, cleaning, analysis, and result export.
    """

    def __init__(self, data_path: str, output_dir: str = "results"):
        """
        Initialize the analysis pipeline.

        Args:
            data_path: Path to the Twitter dataset CSV file
            output_dir: Directory to save results
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Configuration
        self.text_column = "Text"
        self.classification_column = "Biased"
        self.columns_to_keep = [self.text_column, self.classification_column]

        # Pipeline components
        self.data_loader = None
        self.data_cleaner = None
        self.data_analyzer = None

        # Data storage
        self.raw_data = None
        self.cleaned_data = None
        self.analysis_results = None

        logger.info(f"Pipeline initialized for: {self.data_path}")

    def load_data(self) -> None:
        """Load the Twitter dataset."""
        logger.info("=" * 50)
        logger.info("STEP 1: LOADING DATA")
        logger.info("=" * 50)

        try:
            self.data_loader = DataHandler(
                self.data_path,
                encoding='utf-8'
            )

            # Display data info before loading
            data_info = self.data_loader.get_data_info()
            logger.info(f"File size: {data_info['file_size_mb']} MB")

            # Load the data
            self.raw_data = self.data_loader.load_data()

            # Display basic info
            logger.info(f"Loaded data shape: {self.raw_data.shape}")
            logger.info(f"Columns: {list(self.raw_data.columns)}")

            # Check for required columns
            missing_cols = []
            for col in [self.text_column, self.classification_column]:
                if col not in self.raw_data.columns:
                    missing_cols.append(col)

            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            logger.info("✅ Data loaded successfully")

        except Exception as e:
            logger.error(f"❌ Data loading failed: {e}")
            raise

    def clean_data(self) -> None:
        """Clean and preprocess the data."""
        logger.info("=" * 50)
        logger.info("STEP 2: CLEANING DATA")
        logger.info("=" * 50)

        try:
            self.data_cleaner = TextDataCleaner()

            # Apply cleaning pipeline
            self.cleaned_data = self.data_cleaner.clean_pipeline(
                data=self.raw_data,
                text_columns=[self.text_column],
                classification_columns=[self.classification_column],
                remove_unclassified=True
            )

            # Keep only required columns
            self.cleaned_data = self.data_cleaner.keep_only_columns(
                self.cleaned_data,
                self.columns_to_keep
            )

            # Display cleaning statistics
            stats = self.data_cleaner.get_cleaning_stats()
            logger.info(f"Original rows: {stats['original_rows']:,}")
            logger.info(f"Cleaned rows: {stats['cleaned_rows']:,}")
            logger.info(f"Rows removed: {stats['rows_removed']:,}")

            logger.info("✅ Data cleaning completed")

        except Exception as e:
            logger.error(f"❌ Data cleaning failed: {e}")
            raise

    def analyze_data(self) -> None:
        """Perform comprehensive data analysis."""
        logger.info("=" * 50)
        logger.info("STEP 3: ANALYZING DATA")
        logger.info("=" * 50)

        try:
            self.data_analyzer = TextDataAnalyzer(
                data=self.cleaned_data,
                text_column=self.text_column,
                classification_column=self.classification_column
            )

            # Generate comprehensive analysis
            self.analysis_results = self.data_analyzer.generate_comprehensive_analysis()

            # Display summary
            self.data_analyzer.print_analysis_summary(self.analysis_results)

            logger.info("✅ Data analysis completed")

        except Exception as e:
            logger.error(f"❌ Data analysis failed: {e}")
            raise

    def save_results(self) -> None:
        """Save cleaned data and analysis results."""
        logger.info("=" * 50)
        logger.info("STEP 4: SAVING RESULTS")
        logger.info("=" * 50)

        try:
            # Save cleaned dataset
            cleaned_csv_path = self.output_dir / "tweets_dataset_cleaned.csv"
            DataHandler.save_data(
                data=self.cleaned_data,
                file_path=cleaned_csv_path,
                file_type='csv'
            )
            logger.info(f"✅ Cleaned data saved: {cleaned_csv_path}")

            # Save analysis results
            results_json_path = self.output_dir / "results.json"
            self.data_analyzer.save_results(
                file_path=results_json_path,
                results=self.analysis_results
            )
            logger.info(f"✅ Analysis results saved: {results_json_path}")

        except Exception as e:
            logger.error(f"❌ Saving results failed: {e}")
            raise

    def run_complete_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.

        Returns:
            Dict: Analysis results
        """
        logger.info("🚀 STARTING TWITTER ANTISEMITISM ANALYSIS PIPELINE")

        try:
            # Execute pipeline steps
            self.load_data()
            self.clean_data()
            self.analyze_data()
            self.save_results()

            logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")

            return self.analysis_results

        except Exception as e:
            logger.error(f"💥 PIPELINE FAILED: {e}")
            raise

    def get_pipeline_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the pipeline execution.

        Returns:
            Dict: Pipeline execution summary
        """
        summary = {
            'data_path': str(self.data_path),
            'output_dir': str(self.output_dir),
            'pipeline_completed': all([
                self.raw_data is not None,
                self.cleaned_data is not None,
                self.analysis_results is not None
            ])
        }

        if self.raw_data is not None:
            summary['raw_data_shape'] = self.raw_data.shape

        if self.cleaned_data is not None:
            summary['cleaned_data_shape'] = self.cleaned_data.shape

        if self.data_cleaner is not None:
            summary['cleaning_stats'] = self.data_cleaner.get_cleaning_stats()

        return summary


def main():
    """
    Main function to run the Twitter analysis pipeline.
    Modify the data_path to match your file location.
    """
    # Configuration - UPDATE THIS PATH
    DATA_PATH = "data/tweets_dataset.csv"  # Update this path
    OUTPUT_DIR = "results"

    try:
        # Create and run pipeline
        pipeline = TwitterAnalysisPipeline(
            data_path=DATA_PATH,
            output_dir=OUTPUT_DIR
        )

        # Run complete analysis
        results = pipeline.run_complete_pipeline()

        # Display final summary
        summary = pipeline.get_pipeline_summary()
        print("\n" + "=" * 60)
        print("FINAL PIPELINE SUMMARY")
        print("=" * 60)
        print(f"Data processed: {summary['raw_data_shape']} → {summary['cleaned_data_shape']}")
        print(f"Pipeline completed: {summary['pipeline_completed']}")
        print(f"Results saved in: {summary['output_dir']}")
        print("=" * 60)

        return results

    except FileNotFoundError:
        logger.error(f"❌ Data file not found: {DATA_PATH}")
        logger.error("Please update the DATA_PATH variable with the correct file location")
        return None

    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {e}")
        return None


if __name__ == "__main__":
    # Run the main analysis
    analysis_results = main()