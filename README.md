# Бекенд приложения Linehopper

 Локальный запуск:
 
 docker build -t linehopper-backend .
 
 docker run -d -p 8080:8080 linehopper-backend
 
 Поддерживаются запросы:
 
 http://localhost:8080/paths?lat=55.833923&lon=37.626517
 http://localhost:8080/stops?lat=55.833923&lon=37.626517
 
 Также настроен деплой на heroku
 
