import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Класс для вакансий
class Vacancy(BaseModel):
    name: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    region: str
    organization: str
    published_at: datetime
    experience: Optional[str]

# Получение вакансий
def fetch_vacancies(area_id=22, total=2000, per_page=100):
    headers = {'User-Agent': 'hh-parser-app/1.0'}
    all_vacancies = []
    page = 0

    while len(all_vacancies) < total:
        params = {
            'area': area_id,
            'per_page': per_page,
            'page': page
        }
        print(f"Страница {page}...")
        response = requests.get('https://api.hh.ru/vacancies', headers=headers, params=params)
        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            break

        all_vacancies.extend(data['items'])
        page += 1

    return all_vacancies[:total]

# Преобразование в список объектов Vacancy
def process_vacancies(raw_vacancies):
    processed = []

    for item in raw_vacancies:
        salary = item.get('salary')
        vacancy = Vacancy(
            name=item.get('name'),
            salary_from=salary.get('from') if salary else None,
            salary_to=salary.get('to') if salary else None,
            region=item.get('area', {}).get('name'),
            organization=item.get('employer', {}).get('name'),
            published_at=item.get('published_at'),
            experience=item.get('experience', {}).get('name')
        )
        processed.append(vacancy)

    return processed

# Визуализация
def analyze(vacancies):
    df = pd.DataFrame([v.model_dump() for v in vacancies])

    print(f"\nВсего вакансий: {len(df)}")
    print(f"Уникальных работодателей: {df['organization'].nunique()}")

    # Средняя зарплата, если указаны обе границы
    df_salary = df.dropna(subset=['salary_from', 'salary_to']).copy()
    df_salary['salary_from_to'] = (df_salary['salary_from'] + df_salary['salary_to']) / 2

    print(f"Вакансий с полной ЗП: {len(df_salary)}")

    # График
    print('\nГрафик')
    sns.histplot(df_salary['salary_from_to'], kde=True, bins=60)
    plt.xlabel('Средняя зарплата (руб./мес)')
    plt.title('Гистограмма и плотность ЗП')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    raw_data = fetch_vacancies()
    processed_vacancies = process_vacancies(raw_data)
    analyze(processed_vacancies)
