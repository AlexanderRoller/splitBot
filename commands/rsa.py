import schwabdev

def calculate_reverse_split_arbitrage(ticker: str, split_ratio: str, client):
    # Retrieve and parse the JSON data for the given ticker
    data = client.quote(ticker).json()
    ticker_key = ticker.upper()  # Ensure consistency with the JSON data keys
    
    # Verify that data for the ticker exists
    if not data or ticker_key not in data:
        return f"❌ Could not retrieve data for ticker **{ticker_key}**."
    
    # Extract the current price from the "quote" section of the data
    current_price = data[ticker_key].get("quote", {}).get("lastPrice")
    
    if not current_price:
        return f"❌ Could not retrieve the current price for ticker **{ticker_key}**."
    
    # Parse the reverse split ratio provided in the format 'numerator:denominator'
    try:
        split_parts = split_ratio.split(':')
        split_ratio_value = float(split_parts[0]) / float(split_parts[1])
    except (IndexError, ValueError):
        return "⚠️ Invalid split ratio format. Please use 'numerator:denominator'."
    
    # Calculate the profitability of the reverse split arbitrage
    profitability = current_price * (split_ratio_value - 1)
    return f"📈 **Profitability of Reverse Split Arbitrage for {ticker_key}:** ${profitability:.2f}"
