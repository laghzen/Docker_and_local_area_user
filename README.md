# Docker_and_local_area_user

```
Работа с контейнером докера:
  container = StartContainer(mode='create', name=имя_нового_контейнера[, image='base_sandbox' | образ_с докера]) - создание нового контейнера под команду
  container = StartContainer(mode='get', name=имя_существующего_контейнера) - использование контейнера с таким именем

  container.kill() - убирает всю работу контейнера и останавливает его
  container.remove() - удаляет контейнер

  container.load_file(file_in_host=путь_файла_на_хосте, path_in_container=путь_загрузки_файла_в_контейнер[, name_file_in_container=None | имя_файла_в_контейнере]) - загрузка файла в контейнер
  container.download_file(file_in_container=путь_файла_в_контейнере, path_in_host=путь_скачивания_файла_на_хост[, name_file_in_host=None | имя_файла_на_хосте]) - выгрузка файла из контейнера

  container.exec_command(command) - выполнение команд линукса в контейнере с выводом
  container.run_user_code(file_name=имя_файла_с_кодом_игрока[, time_to_slow=3 | время_исполнения_скрипта]) - запускает скрипт игрока с выводом. если он исполняется больше time_to_slow секунд, то убивает его

Весь кипишь и скрипты по пути /sandbox/
```
