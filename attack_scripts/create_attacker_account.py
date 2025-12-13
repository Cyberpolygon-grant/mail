#!/usr/bin/env python3
"""
Автоматизированное создание учетной записи злоумышленника
Этап 2: Создание УЗ внутри системы ДБО
"""

import requests
import json
import time
import random

class DBOAttacker:
    def __init__(self):
        self.operator_session = None
        self.attacker_credentials = None
        self.base_url = "http://localhost"  # URL системы ДБО
        
    def simulate_operator_compromise(self):
        """Симуляция компрометации оператора ДБО #1"""
        
        print("🔴 ЭТАП 2: СОЗДАНИЕ УЗ ЗЛОУМЫШЛЕННИКА")
        print("=" * 50)
        
        print("🎯 Злоумышленник использует reverse shell...")
        print("🔑 Получен доступ к компьютеру operator1@financepro.ru")
        print("💻 Запуск клиента ДБО от имени оператора...")
        
        # Симуляция входа оператора в систему
        self.operator_session = self.login_as_operator()
        
        if self.operator_session:
            print("✅ Успешный вход в систему ДБО как оператор #1")
            return True
        return False
    
    def login_as_operator(self):
        """Симуляция входа оператора в систему"""
        
        # Данные для входа оператора
        operator_data = {
            "email": "operator1@financepro.ru",
            "password": "operator1pass",
            "role": "customer_service"
        }
        
        print(f"🔐 Авторизация: {operator_data['email']}")
        print(f"👤 Роль: {operator_data['role']}")
        
        # Симуляция HTTP запроса
        session_data = {
            "session_id": f"op1_{random.randint(1000, 9999)}",
            "user_id": "operator1",
            "permissions": ["create_client", "view_requests", "manage_accounts"]
        }
        
        print("✅ Сессия оператора создана")
        print(f"🆔 Session ID: {session_data['session_id']}")
        print(f"🔑 Права: {', '.join(session_data['permissions'])}")
        
        return session_data
    
    def create_attacker_account(self):
        """Создание учетной записи злоумышленника"""
        
        print("\n🎯 Создание учетной записи злоумышленника...")
        
        # Данные для создания аккаунта
        attacker_data = {
            "email": "attacker@financepro.ru",
            "password": "attackerpass",
            "full_name": "Иванов Иван Иванович",
            "company": "ООО ТехноИнновации",
            "inn": "1234567890",
            "phone": "+7 (495) 123-45-67",
            "account_type": "corporate",
            "status": "active"
        }
        
        print("📝 Данные нового клиента:")
        for key, value in attacker_data.items():
            print(f"   {key}: {value}")
        
        # Симуляция создания аккаунта
        print("\n🔄 Создание учетной записи...")
        time.sleep(1)
        
        # Генерация учетных данных
        self.attacker_credentials = {
            "client_id": f"CLI_{random.randint(100000, 999999)}",
            "email": attacker_data["email"],
            "password": attacker_data["password"],
            "access_token": f"tok_{random.randint(1000000, 9999999)}",
            "created_by": "operator1",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ Учетная запись злоумышленника создана!")
        print(f"🆔 Client ID: {self.attacker_credentials['client_id']}")
        print(f"📧 Email: {self.attacker_credentials['email']}")
        print(f"🔑 Access Token: {self.attacker_credentials['access_token']}")
        print(f"👤 Создано оператором: {self.attacker_credentials['created_by']}")
        
        return self.attacker_credentials
    
    def login_as_attacker(self):
        """Вход злоумышленника под созданной учетной записью"""
        
        print("\n🎯 Вход злоумышленника в систему...")
        
        if not self.attacker_credentials:
            print("❌ Учетные данные злоумышленника не найдены!")
            return False
        
        # Симуляция входа
        attacker_session = {
            "session_id": f"att_{random.randint(1000, 9999)}",
            "client_id": self.attacker_credentials["client_id"],
            "email": self.attacker_credentials["email"],
            "permissions": ["view_services", "create_requests", "manage_profile"]
        }
        
        print("✅ Злоумышленник успешно вошел в систему!")
        print(f"🆔 Session ID: {attacker_session['session_id']}")
        print(f"👤 Client ID: {attacker_session['client_id']}")
        print(f"🔑 Права: {', '.join(attacker_session['permissions'])}")
        
        return attacker_session
    
    def run_attack_stage_2(self):
        """Запуск этапа 2 атаки"""
        
        print("🚀 ЗАПУСК ЭТАПА 2: СОЗДАНИЕ УЗ ЗЛОУМЫШЛЕННИКА")
        print("=" * 60)
        
        # Компрометация оператора
        if not self.simulate_operator_compromise():
            print("❌ Не удалось получить доступ к оператору")
            return False
        
        # Создание учетной записи
        if not self.create_attacker_account():
            print("❌ Не удалось создать учетную запись злоумышленника")
            return False
        
        # Вход злоумышленника
        attacker_session = self.login_as_attacker()
        if not attacker_session:
            print("❌ Не удалось войти под учетной записью злоумышленника")
            return False
        
        print("\n🎯 ЭТАП 2 ЗАВЕРШЕН УСПЕШНО!")
        print("✅ Злоумышленник получил легитимные учетные данные")
        print("✅ Обход всех процедур проверки и валидации")
        print("✅ Готов к следующему этапу атаки")
        
        return True

if __name__ == "__main__":
    attacker = DBOAttacker()
    attacker.run_attack_stage_2()
