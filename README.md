# Deploy project with Dokcer and DOcker Compose

## Build image

```bash

docker build -t contact-book:latest .
```

## Update Docker Compose with your image

```bash
docker-compose up -d
```

За допомогою цього тестового завдання, ми хочемо зрозуміти, як ви вмієте працювати з вимогами, розбиратись з новими технологіями, інтегрувати ці технології у своєму сервісі. Потрібно створити сервіс з базою контактів, який дозволятиме здійснювати пошук по ним.

1. Створіть PostgreSQL базу даних. Імпортуйте до своєї бази дані з CSV файлу Nimble Contacts (його треба скачати у форматі .csv).

2. Реалізуйте логіку, що буде періодично (наприклад раз на добу) оновлювати контакти у вашій базі з зовнішнього джерела (для цього можете використовувати cron, celery чи будь-яку іншу відому вам технологію). Джерелом даних буде наш продукт - Nimble. Для отримання контактів використовуйте метод:

GET https://api.nimble.com/api/v1/contacts

Документацію по ендпоінту - https://nimble.readthedocs.io/en/latest/contacts/basic/list/. 
Вам будуть потрібні лише поля first name/last name/email/description. Email та description в Nimble - це multiple поля, але для простоти, можете брати лише перше значення. Для автентифікації використовуйте Authorization хедер і токен ("Authorization: Bearer YOUR_API_KEY").
Token  NxkA2RlXS3NiR8SKwRdDmroA992jgu

3. Реалізуйте API з одним методом, що приймає текстову стрічку, за якою відбуватиметься fulltext пошук (https://www.postgresql.org/docs/current/textsearch.html) серед контактів у вашій базі. Бажано не використовувати ORM. У відповідь ваш сервіс повинен повертати список знайдених контактів.

Також приємно було б бачити тести й документацію. Результат треба оформити у вигляді github репозиторію.
