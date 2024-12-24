import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters.command import Command

from config import TOKEN
from weather_service import get_weather_forecasts

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    start_point = State()
    end_point = State()
    intermediate_points = State()
    forecast_days = State()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для прогноза погоды. Используй /weather для получения прогноза.")

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer("Команды:\n/start - Приветствие\n/help - Справка\n/weather - Прогноз погоды")

@dp.message(Command('weather'))
async def cmd_weather(message: types.Message, state: FSMContext):
    await state.set_state(Form.start_point)
    await message.answer("Введите начальную точку маршрута:")

@dp.message(Form.start_point)
async def process_start_point(message: types.Message, state: FSMContext):
    await state.update_data(start_point=message.text)
    await state.set_state(Form.end_point)
    await message.answer("Введите конечную точку маршрута:")

@dp.message(Form.end_point)
async def process_end_point(message: types.Message, state: FSMContext):
    await state.update_data(end_point=message.text)
    await state.set_state(Form.intermediate_points)
    await message.answer("Введите промежуточные точки (через запятую):")

@dp.message(Form.intermediate_points)
async def process_intermediate_points(message: types.Message, state: FSMContext):
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="1"),
                KeyboardButton(text="3"),
                KeyboardButton(text="5")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await state.update_data(intermediate_points=message.text.strip())
    await state.set_state(Form.forecast_days)
    await message.answer(
        "На сколько дней вы хотите получить прогноз? (1-7)",
        reply_markup=keyboard
    )

@dp.message(Form.forecast_days)
async def process_forecast_days(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
        if not 1 <= days <= 7:
            await message.answer("Пожалуйста, введите число от 1 до 7")
            return

        data = await state.get_data()
        route_points = [
            data['start_point'],
            data['end_point']
        ]
        if data['intermediate_points']:
            route_points.extend(point.strip() for point in data['intermediate_points'].split(','))

        forecasts = get_weather_forecasts(route_points, days)

        response_message = ""
        for point, forecast in forecasts.items():
            if forecast:
                response_message += f"Прогноз для {point}:\n"
                for day in forecast['DailyForecasts']:
                    response_message += f"{day['Date']}: Макс. {day['Temperature']['Maximum']['Value']}°C, Мин. {day['Temperature']['Minimum']['Value']}°C\n"
            else:
                response_message += f"Не удалось получить данные для {point}.\n"

        await message.answer(response_message)
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")


@dp.message(F.text)
async def unknown_command(message: types.Message):
    help_text = "Неизвестная команда. Вот доступные команды:\n/start - Приветствие\n/help - Справка\n/weather - Прогноз погоды"
    await message.answer(help_text)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
