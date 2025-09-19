import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import time
import re

def base_search():
    """
    Scrape the stock invested in section from a Moneycontrol fund page
    """
    def scrape_fund_stocks(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table with stock investments
            tables = soup.find_all('table')
            stock_table = None
            
            for table in tables:
                if table.find('th') and 'Stock Invested in' in table.find('th').get_text():
                    stock_table = table
                    break
            
            if not stock_table:
                return []
            
            # Extract stock names from the table
            stocks = []
            rows = stock_table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    stock_name = cells[0].get_text().strip()
                    stocks.append(stock_name)
            
            return stocks
        
        except Exception as e:
            return []

    # URLs of the funds to scrape
    urls = [
        "https://www.moneycontrol.com/mutual-funds/nav/nippon-india-growth-fund-direct-plan/MRC919",
        "https://www.moneycontrol.com/mutual-funds/nav/franklin-india-mid-cap-fund-direct-plan/MTE317",
        "https://www.moneycontrol.com/mutual-funds/nav/edelweiss-mid-cap-fund-direct-plan/MJP117",
        "https://www.moneycontrol.com/mutual-funds/nav/sundaram-mid-cap-fund-direct-plan/MSN568",
        "https://www.moneycontrol.com/mutual-funds/nav/motilal-oswal-midcap-fund-direct-plan/MMO027",
        "https://www.moneycontrol.com/mutual-funds/nav/invesco-india-midcap-fund-direct-plan/MLI556",
        "https://www.moneycontrol.com/mutual-funds/nav/mahindra-manulife-mid-cap-fund-direct-plan-growth/MMH037"
    ]
    
    # Dictionary to store fund names and their stocks
    fund_stocks = {}
    
    # Scrape each fund
    for i, url in enumerate(urls):
        stocks = scrape_fund_stocks(url)
        fund_name = url.split('/')[-2].replace('-', ' ').title()
        fund_stocks[fund_name] = stocks
        time.sleep(1)  # Be polite with delays between requests
    
    # Count stock frequencies across all funds
    all_stocks = []
    for stocks in fund_stocks.values():
        all_stocks.extend(stocks)
    
    stock_frequency = Counter(all_stocks)
    
    # Create a DataFrame for better visualization
    df = pd.DataFrame.from_dict(stock_frequency, orient='index', columns=['Frequency'])
    df = df.sort_values('Frequency', ascending=False)
    
    # Format results
    result = "Stock Frequency Across All Funds:\n"
    result += "=" * 40 + "\n\n"
    
    for stock, count in df.itertuples():
        result += f"{stock}: {count}\n"
    
    result += "\nStocks Appearing in Multiple Funds:\n"
    result += "=" * 40 + "\n\n"
    
    for stock, count in stock_frequency.items():
        if count > 1:
            result += f"{stock}: {count} funds\n"
    
    return result

def advanced_engine_search():
    """
    Scrape all midcap funds and analyze common holdings
    """
    def get_all_midcap_fund_urls():
        url = "https://www.moneycontrol.com/mutual-funds/performance-tracker/returns/mid-cap-fund.html"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all tables
            tables = soup.find_all('table')

            fund_urls = []

            # Look through all tables to find the one with fund data
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue

                # Check if this table has scheme name column
                header_row = rows[0]
                headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]

                if any('scheme' in header.lower() for header in headers):
                    # Extract fund data
                    for row in rows[1:]:
                        cells = row.find_all(['td'])
                        if len(cells) > 0:
                            # First cell should contain fund name and link
                            first_cell = cells[0]
                            link = first_cell.find('a')

                            if link and link.get('href'):
                                fund_url = link.get('href')
                                fund_name = link.get_text(strip=True)

                                # Make sure it's a full URL
                                if fund_url.startswith('/'):
                                    fund_url = 'https://www.moneycontrol.com' + fund_url

                                # Only add if it's a real moneycontrol fund page (not ads)
                                if 'moneycontrol.com/mutual-funds/nav/' in fund_url:
                                    fund_urls.append({
                                        'name': fund_name,
                                        'url': fund_url
                                    })
                    break  # Found the right table, no need to check others

            return fund_urls

        except Exception as e:
            return []

    def scrape_fund_portfolio(url):
        try:
            # Modify URL to get the asset-allocation page
            # Extract fund code from the original URL
            fund_code = url.split('/')[-1]
            base_url = url.rsplit('/', 1)[0]
            portfolio_url = base_url + '/asset-allocation/' + fund_code

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(portfolio_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            stocks = []

            # Look for the stock portfolio table
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                if not rows:
                    continue

                # Check if this table contains stock data
                header_row = rows[0]
                header_cells = header_row.find_all(['th', 'td'])
                header_text = [cell.get_text(strip=True) for cell in header_cells]

                # Look for stock table headers
                if any('Stock Invested in' in header or 'Stock' in header for header in header_text):
                    # Find the index of the stock name column
                    stock_col_index = None
                    for i, header in enumerate(header_text):
                        if 'Stock Invested in' in header or (header == 'Stock' and i == 0):
                            stock_col_index = i
                            break

                    if stock_col_index is not None:
                        # Extract stock names from subsequent rows
                        for row in rows[1:]:
                            cells = row.find_all(['td'])
                            if len(cells) > stock_col_index:
                                stock_name = cells[stock_col_index].get_text(strip=True)

                                # Clean up stock name and filter out non-stock entries
                                if stock_name and not any(skip_word in stock_name.lower() for skip_word in [
                                    'net receivables', 'treps', 'margin', 'cash', 'no new entrants', 
                                    'no complete exits', 'type of instrument', 'particulars'
                                ]):
                                    # Remove company suffixes like Ltd., Limited, etc.
                                    stock_name = re.sub(r'\s+(Ltd\.?|Limited|Corp\.?|Inc\.?|Co\.?)\s*$', '', stock_name, flags=re.IGNORECASE)
                                    if stock_name:
                                        stocks.append(stock_name.strip())

            return list(set(stocks))  # Remove duplicates

        except Exception as e:
            return []

    # Main execution
    result = "Starting comprehensive analysis of ALL mid-cap mutual funds...\n"
    result += "="*80 + "\n\n"

    # Get all midcap fund URLs
    fund_data = get_all_midcap_fund_urls()

    if not fund_data:
        return "No fund URLs found. Exiting."

    result += f"Found {len(fund_data)} funds to analyze\n\n"

    all_stocks = {}

    # Scrape each fund
    for i, fund_info in enumerate(fund_data, 1):
        fund_name = fund_info['name']
        fund_url = fund_info['url']

        stocks = scrape_fund_portfolio(fund_url)
        all_stocks[fund_name] = stocks

        result += f"Scraped fund {i}/{len(fund_data)}: {fund_name} ({len(stocks)} stocks)\n"

        # Add delay to be respectful to the server
        time.sleep(1)

    # Create a list of all unique stocks and count frequencies
    stock_counter = Counter()

    for fund_name, stocks in all_stocks.items():
        for stock in stocks:
            stock_counter[stock] += 1

    # Create results
    total_funds = len(fund_data)
    result += "\n" + "="*80 + "\n"
    result += "ANALYSIS COMPLETE\n"
    result += "="*80 + "\n\n"

    result += f"Total funds analyzed: {total_funds}\n"
    result += f"Total unique stocks found: {len(stock_counter)}\n\n"

    # Show stocks common in all funds
    all_funds_stocks = [stock for stock, count in stock_counter.items() if count == total_funds]
    result += f"Stocks present in ALL {total_funds} funds: {len(all_funds_stocks)}\n"
    if all_funds_stocks:
        for stock in all_funds_stocks:
            result += f"  - {stock}\n"
    result += "\n"

    # Show stocks common in majority of funds
    majority_threshold = total_funds // 2 + 1
    majority_stocks = [stock for stock, count in stock_counter.items() if count >= majority_threshold]
    result += f"Stocks present in {majority_threshold}+ funds (majority): {len(majority_stocks)}\n\n"

    # Show stocks present in at least 25% of funds
    quarter_threshold = max(total_funds // 4, 5)
    popular_stocks = [stock for stock, count in stock_counter.items() if count >= quarter_threshold]
    result += f"Stocks present in {quarter_threshold}+ funds (25%+): {len(popular_stocks)}\n\n"

    # Display top 30 most common stocks
    result += "Top 30 most common stocks across all mid-cap funds:\n"
    result += "="*60 + "\n"
    
    top_30 = stock_counter.most_common(30)
    for i, (stock, count) in enumerate(top_30, 1):
        percentage = (count/total_funds)*100
        result += f"{i:2d}. {stock:<35} ({count:2d} funds - {percentage:.1f}%)\n"

    # Summary statistics
    frequencies = list(stock_counter.values())
    avg_frequency = sum(frequencies) / len(frequencies) if frequencies else 0
    median_frequency = sorted(frequencies)[len(frequencies)//2] if frequencies else 0
    
    result += "\n" + "="*60 + "\n"
    result += "SUMMARY STATISTICS\n"
    result += "="*60 + "\n"
    result += f"Average stock appears in: {avg_frequency:.1f} funds\n"
    result += f"Median stock appears in: {median_frequency:.1f} funds\n"
    result += f"Most popular stock appears in: {max(frequencies) if frequencies else 0} funds\n"
    result += f"Stocks appearing in only 1 fund: {len([f for f in frequencies if f == 1])}\n"

    return result