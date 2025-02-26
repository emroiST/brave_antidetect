import os
import json
import glob


class BraveProfileManager:
    def __init__(self):
        self.brave_path = self._get_brave_path()
        self.local_state_path = os.path.join(self.brave_path, 'Local State')

    def _get_brave_path(self):
    #Определяет путь к папке с данными Brave
        if os.name == 'nt':  # Windows
            return os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data')
        return os.path.expanduser('~/.config/BraveSoftware/Brave-Browser')

    def get_existing_profile_numbers(self):

    #Получает список существующих номеров профилей"""
        profile_pattern = os.path.join(self.brave_path, 'Profile *')
        profiles = glob.glob(profile_pattern)
        numbers = []
        for profile in profiles:
            try:
                name = os.path.basename(profile).replace('Profile ', '')
                if name.isdigit():
                    numbers.append(int(name))
            except ValueError:
                continue
        return sorted(numbers)

    def get_next_profile_number(self):

    #Определяет следующий доступный номер профиля
        existing_numbers = self.get_existing_profile_numbers()
        if not existing_numbers:
            return 1
        for i in range(1, max(existing_numbers) + 2):
            if i not in existing_numbers:
                return i

    def update_local_state(self, profile_number):

    #Обновляет Local State для отображения профиля в браузере
        try:
            if os.path.exists(self.local_state_path):
                with open(self.local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
            else:
                local_state = {}
            if 'profile' not in local_state:
                local_state['profile'] = {}
            if 'info_cache' not in local_state['profile']:
                local_state['profile']['info_cache'] = {}
            profile_id = f'Profile {profile_number}'
            local_state['profile']['info_cache'][profile_id] = {
                'name': str(profile_number),
                'is_using_default_name': False,
                'is_using_default_avatar': True,
                'avatar_icon': '0',
                'name_is_ephemeral': False,
                'background_apps': False
            }
            with open(self.local_state_path, 'w', encoding='utf-8') as f:
                json.dump(local_state, f, indent=4)

        except Exception as e:
            print(f"Ошибка при обновлении Local State: {str(e)}")

    def create_profile_preferences(self, profile_number):

    #Создает файл настроек профиля с особыми параметрами приватности
        return {
            "profile": {
                "name": str(profile_number),
                "avatar_icon": "0",
            },
            "browser": {
                "custom_chrome_frame": False,
                "show_home_button": False,
            },
            "webrtc": {
                "multiple_routes_enabled": False,
                "non_proxied_udp_enabled": False,
                "ip_handling_policy": "disable_non_proxied_udp"
            },
        }

    def create_profile(self):

    #Создает новый профиль с последовательной нумерацией
        profile_number = self.get_next_profile_number()
        profile_name = str(profile_number)
        new_profile_path = os.path.join(self.brave_path, f'Profile {profile_name}')

        if os.path.exists(new_profile_path):
            raise Exception(f'Профиль {profile_name} уже существует')

        os.makedirs(new_profile_path)
        preferences = self.create_profile_preferences(profile_number)
        preferences_path = os.path.join(new_profile_path, 'Preferences')
        with open(preferences_path, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=4)
        self.update_local_state(profile_number)
        return new_profile_path

    def ensure_profile_count(self, target_count):
    #Проверяет текущее количество профилей и создает новые до достижения целевого количества

        existing_numbers = self.get_existing_profile_numbers()
        current_count = len(existing_numbers)
        profiles_to_create = max(0, target_count - current_count)
        created_profiles = []
        for _ in range(profiles_to_create):
            new_profile = self.create_profile()
            created_profiles.append(new_profile)
        return created_profiles


if __name__ == "__main__":
    manager = BraveProfileManager()
    try:
        # Указываем желаемое количество профилей
        target_profiles = 5
        new_profiles = manager.ensure_profile_count(target_profiles)

        if new_profiles:
            print(f"Создано {len(new_profiles)} новых профилей:")
            for profile in new_profiles:
                print(f"- {profile}")
            print("\nПрофили успешно добавлены в Local State и должны отображаться при запуске Brave")
            print("Перезапустите браузер, чтобы увидеть новые профили")
        else:
            existing = manager.get_existing_profile_numbers()
            print(f"Новые профили не требуются. Существующие профили: {existing}")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
