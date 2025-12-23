from commands.formatting import format_response
from commands.economic_calendar import summarize_weekly_calendar
from commands.price import get_stock_price
from commands.health import get_server_status
from commands.rsa import calculate_reverse_split_arbitrage

async def test_all(ctx):
    """
    Test all bot commands with sample inputs.
    """
    # Example inputs for testing
    test_ticker = "AAPL"  # Example ticker symbol for stock price
    test_split_ratio = "2:1"  # Example reverse split ratio

    # Test stock price command
    stock_price_response = get_stock_price(test_ticker).replace(
        f"**Price for {test_ticker}**",
        f"**Price for {test_ticker} (!price {test_ticker})**",
    )
    await ctx.send(stock_price_response)

    # Test health check command
    server_health_response = get_server_status().replace(
        "**Server Health**",
        "**Server Health (!health)**",
    )
    await ctx.send(server_health_response)

    # Test reverse split arbitrage command
    rsa_response = calculate_reverse_split_arbitrage(test_ticker, test_split_ratio).replace(
        f"**Reverse Split Arbitrage for {test_ticker}**",
        f"**Reverse Split Arbitrage for {test_ticker} (!rsa {test_ticker} {test_split_ratio})**",
    )
    await ctx.send(rsa_response)

    # Test economic calendar command
    calendar_response = summarize_weekly_calendar(include_command=True)
    await ctx.send(calendar_response)

    await ctx.send(format_response("Test Run Complete", ["All checks finished."]))
