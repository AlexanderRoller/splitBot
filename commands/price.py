import schwabdev
import json

def get_stock_price(ticker: str, client):
    # Retrieve and parse the JSON data for the given ticker
    data = client.quote(ticker).json()
    ticker_key = ticker.upper()  # Ensure the ticker key matches the data (e.g., "AAPL")
    
    # Optionally, save the raw data to a JSON file 
    # with open(f"data_{ticker_key}.json", "w") as file:
    #     json.dump(data, file, indent=4)
    
    # Check if data exists and the expected ticker key is present
    if data and ticker_key in data:
        # Access the "quote" dictionary within the ticker's data
        quote_data = data[ticker_key].get("quote", {})
        # Extract the lastPrice value from the quote data
        last_price = quote_data.get("lastPrice")
        
        if last_price is not None:
            response = (
                f"💹 **Current Price of {ticker_key}** 💹\n"
                f"💲 **Price:** **${last_price:.2f}**\n"
                "Keep an eye on the market! 📈"
            )
        else:
            response = f"❌ Could not retrieve the last price for ticker **{ticker_key}**."
    else:
        response = f"❌ Could not retrieve data for ticker **{ticker_key}**."
    
    return response