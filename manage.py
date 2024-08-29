import asyncio
import logging
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from currency_request import exchange_rate

# Load environment variables from .env file
load_dotenv()

# Configure logging settings
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("bot.log"),
                        logging.StreamHandler()
                    ])

# Create a logger instance
logger = logging.getLogger(__name__)

# Retrieve API keys and bot token from environment variables
exchange_rate_api_key = os.getenv('API_KEY')
logs_key = os.getenv('LOGS_KEY')
bot = Bot(token=os.getenv("TOKEN"))

# Create a dispatcher for handling bot updates
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message):
    """
        This function handles the '/start' command. It logs the user's ID and sends a welcome message.

        Parameters:
        message (aiogram.types.Message): The incoming message object containing the user's ID and command.

        Returns:
        None
        """
    user_id = message.from_user.id
    logger.info(f"User {user_id} issued /start command")
    await message.answer("Hello! This bot was created to receive information on world currency rates")


@dp.message(Command("currency"))
async def cmd_currency(message, command):
    """
        This function handles the '/currency' command. It retrieves and sends the exchange rate of a specified currency.
        If two currencies are provided, it calculates the conversion rate between them.

        Parameters:
        message (aiogram.types.Message): The incoming message object containing the user's ID and command.
        command (aiogram.types.Command): The command object containing the command and its arguments.

        Returns:
        None
        """
    user_id = message.from_user.id
    currency_code = command.args.upper() if command.args else None
    if currency_code:
        if ' ' in currency_code:
            currency_code1, currency_code2 = currency_code.split()
            conversion_rate, time_last_update_utc = exchange_rate(currency_code1, currency_code2, exchange_rate_api_key)
            logger.info(f"User {user_id} requested currency: {currency_code1}, {currency_code2}")
        else:
            conversion_rate, time_last_update_utc = exchange_rate(currency_code, api_key=exchange_rate_api_key)
            logger.info(f"User {user_id} requested currency: {currency_code}\nLast update: {time_last_update_utc[:-15:]}")

        if conversion_rate is not None:
            await message.answer(f"You've entered currency: {conversion_rate}\nLast update: {time_last_update_utc[:-15:]}")
        else:
            logger.warning(f"User {user_id} did not provide a currency code")
            await message.answer(
                "Please enter a currency code after the command, e.g., /currency USD or /currency USD EUR.")
    else:
        logger.warning(f"User {user_id} did not provide a currency code")
        await message.answer(
            "Please enter a currency code after the command, e.g., /currency USD or /currency USD EUR.")


@dp.message(Command("log"))
async def cmd_log(message, command):
    """
        This function handles the '/log' command. It checks if the provided key matches the logs key,
        and if so, it sends the bot.log file as a document message.

        Parameters:
        message (aiogram.types.Message): The incoming message object containing the user's ID and command.
        command (aiogram.types.Command): The command object containing the command and its arguments.

        Returns:
        None
        """
    key = command.args
    user_id = message.from_user.id
    if key == logs_key:
        logger.info(f"User {user_id} requested logs")
        file = types.FSInputFile("bot.log")
        await message.answer_document(file)

async def main():
    logger.info("Bot started polling")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
    finally:
        logger.info("Bot stopped polling")


if __name__ == "__main__":
    asyncio.run(main())
