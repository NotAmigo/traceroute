# Traceroute
###### Авторы: Ковальчук Илья, Пестов Владимир
###### Группа: ФТ-202
___

### Описание
##### Программа предназначена для отслеживания маршрута до указанного хоста. Программа работает с протоколом ICMP. Программа работает в нескольких режимах:
* Режим 1: Отслеживание маршрута до указанного хоста
* Режим 2: Отслеживание маршрута до указанного хоста с указанием максимального количества прыжков
* Режим 3: Отслеживание маршрута до указанного хоста с указанием максимального количества прыжков и указанием интервала между прыжками
* Режим 4: Отслеживание маршрута до указанного хоста с указанием максимального количества прыжков и указанием интервала между прыжками и указанием размера пакета
* Режим 5: Отслеживание маршрута до указанного хоста с указанием максимального количества прыжков и указанием интервала между прыжками и указанием размера пакета и указанием TTL
___

### Требования
* Python 3.11
* Модули из файла requirements.txt
___

### Состав проекта
* **traceroute.py** - основной файл программы
* **main.py** - файл для запуска программы
* **ping.py** - файл с реализацией функции ping
* **requirements.txt** - файл с зависимостями
* **readme.md** - файл с описанием проекта
* **.gitignore** - файл с игнорируемыми файлами
____

### Алгоритм запуска
Запуск: python ./main.py [параметры]
###### Для просмотра справки запустите программу с параметром --help
____