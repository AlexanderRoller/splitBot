import asyncio

import discord

from commands.chart import generate_stock_chart
from commands.formatting import format_response
from commands.health import get_server_status
from commands.price import get_stock_price
from commands.rsa import calculate_reverse_split_arbitrage


async def test_all(ctx):
    """
    Test all bot commands with sample inputs.
    """
    test_ticker = "AAPL"
    test_split_ratio = "1:10"

    stock_price_response = (await asyncio.to_thread(get_stock_price, test_ticker)).replace(
        f"**Price for {test_ticker}**",
        f"**Price for {test_ticker} (!price {test_ticker})**",
    )
    await ctx.send(stock_price_response)

    server_health_response = (await asyncio.to_thread(get_server_status)).replace(
        "**Server Health**",
        "**Server Health (!health)**",
    )
    await ctx.send(server_health_response)

    rsa_response = (await asyncio.to_thread(calculate_reverse_split_arbitrage, test_ticker, test_split_ratio)).replace(
        f"**Reverse Split Arbitrage for {test_ticker}**",
        f"**Reverse Split Arbitrage for {test_ticker} (!rsa {test_ticker} {test_split_ratio})**",
    )
    await ctx.send(rsa_response)

    chart_stream, filename, caption, chart_error = await asyncio.to_thread(
        generate_stock_chart,
        test_ticker,
        "1mo",
    )
    if chart_error:
        await ctx.send(chart_error)
    elif chart_stream is not None:
        try:
            await ctx.send(content=caption, file=discord.File(fp=chart_stream, filename=filename))
        finally:
            chart_stream.close()

    await ctx.send(format_response("Test Run Complete", ["All checks finished."]))
