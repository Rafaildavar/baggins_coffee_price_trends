from typing import  Optional
import pandas as pd
from typing import Dict
from _datetime import datetime
# Задаем путь к файлу CSV
file_path = '../sorted_customers.csv'  # Замените на путь к вашему файлу

# Читаем данные из CSV файла
df = pd.read_csv(file_path)
# Выводим данные
df = df.drop(columns=['purchases_per_week'])


def get_customer_info(customer_id: int) -> Optional[pd.Series]:
    """
    Получает информацию о клиенте по его customer_id.

    :param customer_id: ID клиента
    :return: Строка из DataFrame с данными клиента или None, если ID не найден
    """
    customer_row = df[df['customer_id'] == customer_id]
    return customer_row.iloc[0] if not customer_row.empty else None

def generate_recommendations(customer_data: Dict) -> Dict:
    """
    Генерирует рекомендации для пользователя на основе его данных.

    :param customer_data: Словарь с характеристиками пользователя
    :return: Словарь с рекомендациями
    """
    recommendations = {}
    # Определяем текущий месяц
    current_month = datetime.now().month

    # Определяем стратегию в зависимости от классификации клиента
    if customer_data['customer_classification'] == 'Редкий':
        #recommendations['strategy'] = 'Акции для редких клиентов'
        recommendations['message'] = "Вы делаете покупки нечасто. Получите подарок к следующему заказу, чтобы сделать процесс приятнее!"
    elif customer_data['customer_classification'] == 'Новый':
       # recommendations['strategy'] = "Акции для Новых клиентов"
        recommendations['message'] = "Добро пожаловать! Мы рады видеть вас среди наших клиентов. Получите скидку 10% на первую покупку."
    elif customer_data['customer_classification'] == 'Регулярный':
       # recommendations['strategy'] = "Акции для Регулярных клиентов"
        recommendations['message'] = f"Спасибо за вашу преданность! Получите скидку на ваш любимый товар{customer_data["favority_entity_id"]}!"
    elif customer_data['customer_classification'] == 'Постоянных':
        recommendations['strategy'] = "Акции для Постоянных клиентов"
        recommendations['message'] =  f"Мы ценим вашу лояльность! Наслаждайтесь эксклюзивной акцией 5ое кофе в подарок. Только до конца недели]"
     # Рекомендации на основе среднего количества товаров в заказе
    #if customer_data['avg_products_per_order'] < 2:
        #recommendations['bundle_offer'] = 'Предложите комплект товаров со скидкой.'

    # Используем время и сезон для таргетированных предложений
    # Утренние скидки
    if customer_data['most_frequent_time'] == 1:
        recommendations['time_based_offer'] = '🌅 Утренние скидки: заказывайте два кофе до 12:00 и получите скидку 10%!'

    # Обеденные скидки
    if customer_data['most_frequent_time'] == 4:
        recommendations[
            'time_based_offer'] = '🍴 Обеденные скидки: с 12:00 до 14:00 закажите ланч и получите десерт в подарок!'

    # Дневные скидки
    if customer_data['most_frequent_time'] == 2:
        recommendations['time_based_offer'] = '☀️ Дневные предложения: с 14:00 до 17:00 скидка 15% на ваши любимые напитки!'

    # Вечерние скидки
    if customer_data['most_frequent_time'] == 3:
        recommendations['time_based_offer'] = '🌙 Вечерние скидки: после 17:00 заказывайте кофе и выпечку со скидкой 20%!'

    # Условия для реактивации по времени года
    if customer_data['days_since_last_purchase'] > 180:
        # Зима: Декабрь (12), Январь (1), Февраль (2)
        if current_month in [12, 1, 2] and customer_data['most_frequent_season'] == 3:
            recommendations[
                'seasonal_reactivation'] = "❄️ Зима без вас? Это слишком холодно! Закажите сейчас и получите горячий напиток со скидкой 25%."
        # Весна: Март (3), Апрель (4), Май (5)
        elif current_month in [3, 4, 5] and customer_data['most_frequent_season'] == 4:
            recommendations[
                'seasonal_reactivation'] = "🌸 Весна — время нового начала! Скидка 20% на первый заказ этой весной, только для вас!"
        # Лето: Июнь (6), Июль (7), Август (8)
        elif current_month in [6, 7, 8] and customer_data['most_frequent_season'] == 2:
            recommendations[
                'seasonal_reactivation'] = "☀️ Лето не может быть без холодных напитков! Вернитесь к нам и получите скидку 15% на любой фраппе."
        # Осень: Сентябрь (9), Октябрь (10), Ноябрь (11)
        elif current_month in [9, 10, 11] and customer_data['most_frequent_season'] == 1:
            recommendations[
                'seasonal_reactivation'] = "🍂 Осенний уют ждёт вас! Закажите сейчас и получите 10% скидку на кофе с выпечкой."

    # Общие сезонные предложения (актуальны только для текущего времени года)
    # Зима
    if current_month in [12, 1, 2] and customer_data['most_frequent_season'] == 3:
        recommendations[
            'seasonal_offer'] = '❄️ Зимняя акция: согревающие напитки со скидкой 25% для холодных дней!'
    # Весна
    elif current_month in [3, 4, 5] and customer_data['most_frequent_season'] == 4:
        recommendations['seasonal_offer'] = '🌸 Весенняя распродажа: скидка 20% на первую покупку этой весной!'
    # Лето
    elif current_month in [6, 7, 8] and customer_data['most_frequent_season'] == 2:
        recommendations['seasonal_offer'] = '☀️ Летние предложения: освежающие холодные напитки со скидкой 15%!'
    # Осень
    elif current_month in [9, 10, 11] and customer_data['most_frequent_season'] == 1:
        recommendations['seasonal_offer'] = '🍂 Осенний уют: горячие напитки и пироги со скидкой 10%!'

    # Условия для реактивации неактивных клиентов
    if 30 <= customer_data['days_since_last_purchase'] <= 90:
        recommendations['reactivation_offer'] = "Давно не виделись! Возвращайтесь к нам и получите скидку 15% на следующую покупку!"
    elif 91 <= customer_data['days_since_last_purchase'] <= 180:
        recommendations['reactivation_offer'] = "Мы скучаем по вам! Чтобы встреча была приятной, мы дарим вам 20% скидку на кофе и десерты."
    elif 181 <= customer_data['days_since_last_purchase'] <= 365:
        recommendations['reactivation_offer'] = "Год без вашего любимого кофе — это слишком! Возвращайтесь, и получите подарок к первому заказу!"
    elif customer_data['days_since_last_purchase'] > 365:
        recommendations['reactivation_offer'] = f"Мы скучаем по вам! Ваш любимый {customer_data['favority_entity_id']} ждёт вас со скидкой 30%!"
        # Условия для постоянных клиентов
    if customer_data['days_since_last_purchase'] > 365 and customer_data['customer_classification'] in ['Регулярный', 'Постоянный']:
        recommendations['loyalty_offer'] = "Вы были нашим частым гостем, и мы это ценим! Получите бонусный кофе к следующему заказу."
    # Условия для крупных заказов
    if customer_data['days_since_last_purchase'] > 365 and customer_data['avg_products_per_order'] > 3:
        recommendations['bulk_discount'] = "Мы скучали по вашим большим заказам! Скидка 20% на любой заказ из 4 и более товаров."
    return recommendations



