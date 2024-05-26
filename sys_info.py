import sys
import psutil
import platform
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget, QComboBox, QLabel
from PySide6.QtCore import QTimer


class SystemMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Мониторинг системы')

        # Создаем виджет для содержимого
        content_widget = QWidget()
        self.setCentralWidget(content_widget)

        # Метки для отображения общей информации о системе и количества процессов/служб
        self.system_info_label = QLabel()
        self.processes_label = QLabel()
        self.services_label = QLabel()
        self.scheduler_tasks_label = QLabel()

        # Текстовые браузеры для детальной информации
        self.processes_browser = QTextBrowser()
        self.services_browser = QTextBrowser()
        self.scheduler_tasks_browser = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.system_info_label)
        layout.addWidget(self.processes_label)
        layout.addWidget(self.processes_browser)
        layout.addWidget(self.services_label)
        layout.addWidget(self.services_browser)
        layout.addWidget(self.scheduler_tasks_label)
        layout.addWidget(self.scheduler_tasks_browser)
        content_widget.setLayout(layout)

        # Комбо-бокс для выбора интервала обновления
        self.update_interval_combo = QComboBox()
        self.update_interval_combo.addItems(["1 сек", "5 сек", "10 сек", "30 сек"])
        self.update_interval_combo.currentIndexChanged.connect(self.update_interval_changed)
        layout.addWidget(self.update_interval_combo)

        # Настройка таймера для обновления информации
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.update_interval = 5000  # По умолчанию обновление каждые 5 секунд

        self.update_interval_combo.setCurrentIndex(1)  # Устанавливаем начальный интервал обновления

        self.update_system_info()

    def update_system_info(self) -> None:
        """
        Функция получает и обновляет информацию о системе
        :return: None
        """
        # Получаем информацию о системе
        cpu_name = platform.processor()
        cpu_cores = psutil.cpu_count()
        cpu_load = psutil.cpu_percent()
        mem_total = psutil.virtual_memory().total // (1024 ** 3)
        mem_used = psutil.virtual_memory().used // (1024 ** 3)
        mem_free = psutil.virtual_memory().free // (1024 ** 3)
        disks_info = self.get_disks_info()

        # Обновляем метки с общей информацией о системе и количеством процессов/служб
        self.system_info_label.setText(f"Процессор: {cpu_name}, Ядер: {cpu_cores}, Загрузка: {cpu_load}%\n"
                                       f"Оперативная память: {mem_total} GB, Использовано: {mem_used} GB,"
                                       f" Свободно: {mem_free} GB\n{disks_info}")

        processes = [p.name() for p in psutil.process_iter(['pid', 'name'])]
        self.processes_label.setText(f"Работающие процессы: {len(processes)}")
        self.services_label.setText(f"Работающие службы:"
                                    f" {len([service.name() for service in psutil.win_service_iter()])}")

        # Обновляем текстовые браузеры с детальной информацией
        self.processes_browser.clear()
        self.processes_browser.append("\n".join(processes))
        if hasattr(psutil, 'win_service_iter'):
            services = [service.name() for service in psutil.win_service_iter()]
            self.services_browser.clear()
            self.services_browser.append("\n".join(services))
        else:
            self.services_browser.append("Работающие службы: Не поддерживается")
        try:
            scheduler_tasks = subprocess.check_output(["systemctl", "status"]).decode("utf-8").split("\n")[7:]
            self.scheduler_tasks_browser.clear()
            self.scheduler_tasks_browser.append("\n".join(scheduler_tasks[:10]))

        except Exception as e:
            self.scheduler_tasks_browser.clear()
            self.scheduler_tasks_browser.append("Задачи планировщика: Информация недоступна")

    def get_disks_info(self) -> str:
        """
        Функция получает и обновляет информацию о дисках
        :return: Информация о дисках
        """
        disks_info = ""
        for i, part in enumerate(psutil.disk_partitions()):
            if not part.mountpoint == "/":
                fs_stat = psutil.disk_usage(part.mountpoint)
                total_gb = fs_stat.total // (1024 ** 3)
                used_gb = fs_stat.used // (1024 ** 3)
                free_gb = fs_stat.free // (1024 ** 3)
                disks_info += f"Диск {i}: {part.device} - Объем: {total_gb} GB, Занято: {used_gb} GB," \
                              f" Свободно: {free_gb} GB\n"
        return disks_info

    def update_interval_changed(self, index) -> None:
        """
        Функия обновляет данные в зависимости от выбранного интервала времени.
        :param index: интервал задержки выбранное пользователем.
        :return: None
        """
        intervals = ["1000", "5000", "10000", "30000"]
        self.timer.stop()
        self.timer.setInterval(int(intervals[index]))
        self.timer.start()


if __name__ == "__main__":
    app = QApplication([])
    window = SystemMonitorApp()
    window.show()
    app.exec()
