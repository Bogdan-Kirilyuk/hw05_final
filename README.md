# Социальная сеть для публикации личных дневников

    Реализована регистрация пользователя, публикация постов, подписки/отписки на авторов, комментирование постов, добавление картинок. Записи можно отправить в сообщество и посмотреть там записи разных авторов.

- 1. В проект добавлены кастомные страницы ошибок:
404 page_not_found
500 server_error
403 permission_denied_view
Написан тест, проверяющий, что страница 404 отдает кастомный шаблон.
- 2. С помощью sorl-thumbnail выведены иллюстрации к постам:
в шаблон главной страницы,
в шаблон профайла автора,
в шаблон страницы группы,
на отдельную страницу поста.
- 3. Создана система комментариев
Написана система комментирования записей. На странице поста под текстом записи выводится форма для отправки комментария, а ниже — список комментариев. Комментировать могут только авторизованные пользователи. Работоспособность модуля протестирована.
- 4. Кеширование главной страницы
Список постов на главной странице сайта хранится в кэше и обновляется раз в 20 секунд.
- 5. Тестирование кэша
Написан тест для проверки кеширования главной страницы. Логика теста: при удалении записи из базы, она остаётся в response.content главной страницы до тех пор, пока кэш не будет очищен принудительно.нная оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.

- 6. Написаны тесты, которые проверяют:
при выводе поста с картинкой изображение передаётся в словаре context
на главную страницу,
на страницу профайла,
на страницу группы,
на отдельную страницу поста;
при отправке поста с картинкой через форму PostForm создаётся запись в базе данных;
#### Не забывай делать следующие штуки:
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
```
```
source venv/Scripts/activate
```
- Установить зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Для запуска проекта, в папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```

- ✨Magic ✨
