AntiSpamBot - бот, отлавливающий спам ботов в телеграмм чате и предотвращающий последствия их нахождения в чате 


Установка бота: посде добавления бота в чат необходимо выдать
права администратора (включение в них "Удаление сообщений" и "Блокировка участников")

Запуск бота: для запуска бота в конкретном чате необходимо в чат отправить команду
/start (только после этой команды можно управлять ботом)

Доступные команды для настройки бота:
/help — для вызова сообщения со всеми доступными командами

/captcha — для смены типа капчи (кнопка, арифметический пример, цыфры с картинки)

/no_enter_mess — команда, которая будет удалять сообщения о всходе новых пользователей

/enter_mess — команда, которая не будет удалять сообщения о всходе новых пользователей

/attack — включение проверки новых пользователей на бота

/no_attack — отключение проверки новых пользователей на бота

/list_of_links — вывести список доступных ссылок, которые любые пользователи могут отправлять

/add_links — добавить ссылки в список доступных ссылок

/links — разрешить всем пользователям отправлять сообщения с ссылками

/no_links — запретить всем пользователям отправлять сообщения с ссылками (кроме тех, которые находятся в списке доступных)

/start — для запуска бота


Особенности: бот не удаляет ссылок, которые отправлены администраторами. Чтобы добавить ссылки с список доступных, необходимо отправить их
в ответ на сообщение которое отправится после ввода команды /add_links. Бот реагирует только на команды администраторов (обычные пользователи
не могут управлять ботом)
