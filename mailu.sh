#!/bin/bash
# Единый скрипт управления Mailu + фишинговая атака

echo "🎯 MAILU + ФИШИНГОВАЯ АТАКА"
echo "=========================="

show_help() {
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "КОМАНДЫ:"
    echo "  start     - Запустить Mailu с фишинговой атакой"
    echo "  stop      - Остановить все сервисы"
    echo "  logs      - Показать логи фишинговой атаки"
    echo "  status    - Показать статус сервисов"
    echo "  users     - Создать всех пользователей"
    echo "  clean     - Остановить и удалить все"
    echo "  help      - Показать эту справку"
    echo ""
    echo "ПРИМЕРЫ:"
    echo "  $0 start    # Запустить систему"
    echo "  $0 users    # Создать пользователей"
    echo "  $0 logs     # Просмотр логов"
    echo "  $0 stop     # Остановить"
}

build_and_start() {
    echo "🚀 Запуск Mailu с фишинговой атакой..."
    echo "🔨 Сборка образа..."
    docker compose build phishing-demo
    echo "📦 Запуск сервисов..."
    docker compose --profile phishing up -d
    echo "✅ Система запущена"
    echo "🌐 Веб-почта: http://financepro.ru/webmail/"
    echo "🔧 Админка: http://financepro.ru/admin/"
}

create_users() {
    echo "👤 Создание пользователя operator1..."
    sleep 5
    echo "📧 Создание: operator1@financepro.ru"
    docker compose exec admin flask mailu user operator1 financepro.ru '1q2w#E$R' 2>/dev/null || echo "   ⚠️  Уже существует"
    
    # Отключаем требование смены пароля при первом входе
    echo "🔧 Отключение требования смены пароля при первом входе..."
    docker compose exec admin python3 -c "
import sqlite3
db_path = '/data/main.db'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Устанавливаем change_pw_next_login в 0 (False)
    cursor.execute('UPDATE \"user\" SET change_pw_next_login = 0 WHERE email = ?', ('operator1@financepro.ru',))
    conn.commit()
    conn.close()
    print('✅ Требование смены пароля отключено')
except Exception as e:
    print(f'⚠️  Ошибка: {e}')
" 2>/dev/null || echo "   ⚠️  Не удалось отключить требование смены пароля"
    echo ""
    
    echo "✅ Пользователь создан"
    echo ""
    echo "👤 УЧЕТНАЯ ЗАПИСЬ:"
    echo "   operator1@financepro.ru / 1q2w#E$R - Оператор ДБО #1 (жертва)"
    echo ""
    echo "🌐 ДОСТУП К ПОЧТЕ:"
    echo "   Веб-интерфейс: http://financepro.ru/webmail"
    echo "   Админка: http://financepro.ru/admin"
}

show_logs() {
    echo "📊 Логи фишинговой атаки:"
    docker compose logs phishing-demo
}

show_status() {
    echo "📋 Статус сервисов:"
    docker compose ps
}

stop_all() {
    echo "🛑 Остановка всех сервисов..."
    docker compose --profile phishing down
    echo "✅ Все сервисы остановлены"
}

clean_all() {
    echo "🧹 Полная очистка системы..."
    echo "1. Остановка всех контейнеров..."
    docker compose down
    echo "2. Удаление данных Mailu..."
    sudo rm -rf /mailu/
    echo "3. Удаление образов..."
    docker compose down -v
    echo "✅ Система полностью очищена"
}

case "${1:-help}" in
    "start")
        build_and_start
        ;;
    "users")
        create_users
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "stop")
        stop_all
        ;;
    "clean")
        clean_all
        ;;
    "help"|*)
        show_help
        ;;
esac
