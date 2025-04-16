import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import os

from .sec_crawler import SECFilingCrawler
from .report_generator import ReportGenerator

class SECParserApp:
    def __init__(self, user_agent: str, output_dir: str = "reports"):
        """
        Initialize the SEC Parser application.
        
        Args:
            user_agent: Your user agent string
            output_dir: Directory to save reports
        """
        self.crawler = SECFilingCrawler(user_agent)
        self.report_generator = ReportGenerator(output_dir)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_company(self, cik: str, form_type: str = "10-K", 
                       start_date: datetime = None,
                       end_date: datetime = None) -> List[str]:
        """
        Process filings for a specific company.
        
        Args:
            cik: Company CIK number
            form_type: Type of filing
            start_date: Start date for filings
            end_date: End date for filings
            
        Returns:
            List of paths to generated reports
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        self.logger.info(f"Processing {form_type} filings for CIK {cik}")
        
        # Get filings
        filings = self.crawler.get_company_filings(
            cik, form_type, start_date, end_date
        )
        
        if not filings:
            self.logger.warning(f"No filings found for CIK {cik}")
            return []
        
        report_paths = []
        for filing in filings:
            try:
                # Download filing
                filing_url = self.crawler.get_filing_url(cik, filing['accession_number'])
                content = self.crawler.download_filing(filing_url)
                
                if not content:
                    self.logger.warning(f"Failed to download filing {filing['accession_number']}")
                    continue
                
                # Generate report
                report = self.report_generator.generate_report(content, filing)
                
                # Save report
                report_path = self.report_generator.save_report(report, format='json')
                report_paths.append(report_path)
                
                self.logger.info(f"Generated report: {report_path}")
                
            except Exception as e:
                self.logger.error(f"Error processing filing {filing['accession_number']}: {e}")
        
        return report_paths
    
    def process_companies(self, ciks: List[str], form_type: str = "10-K",
                         start_date: datetime = None,
                         end_date: datetime = None) -> Dict[str, List[str]]:
        """
        Process filings for multiple companies.
        
        Args:
            ciks: List of company CIK numbers
            form_type: Type of filing
            start_date: Start date for filings
            end_date: End date for filings
            
        Returns:
            Dictionary mapping CIKs to their report paths
        """
        results = {}
        for cik in ciks:
            report_paths = self.process_company(
                cik, form_type, start_date, end_date
            )
            results[cik] = report_paths
        return results

def main():
    parser = argparse.ArgumentParser(description='SEC Filing Parser')
    parser.add_argument('--cik', required=True, help='Company CIK number')
    parser.add_argument('--form-type', default='10-K', help='Type of filing (e.g., 10-K, 10-Q)')
    parser.add_argument('--user-agent', required=True, help='Your user agent string')
    parser.add_argument('--output-dir', default='reports', help='Output directory for reports')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d') if args.start_date else None
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d') if args.end_date else None
    
    # Create and run app
    app = SECParserApp(args.user_agent, args.output_dir)
    app.process_company(args.cik, args.form_type, start_date, end_date)

if __name__ == "__main__":
    main() 