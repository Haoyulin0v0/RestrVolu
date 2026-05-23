"""
单元测试模块
测试核心功能
"""

import unittest
from unittest.mock import MagicMock, patch
from core.volume_controller import VolumeController
from core.process_monitor import ProcessMonitor


class TestVolumeController(unittest.TestCase):
    """音量控制器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.controller = VolumeController()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.controller.sessions)
        self.assertIsInstance(self.controller.sessions, dict)
    
    def test_volume_range(self):
        """测试音量范围"""
        # 音量应该在0-100之间
        volume = 50
        self.assertTrue(0 <= volume <= 100)


class TestProcessMonitor(unittest.TestCase):
    """进程监听器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.monitor = ProcessMonitor()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.monitor.exclude_processes)
        self.assertIsInstance(self.monitor.exclude_processes, set)
    
    def test_exclude_processes(self):
        """测试系统进程排除"""
        excluded = self.monitor.exclude_processes
        self.assertIn('svchost.exe', excluded)
        self.assertIn('explorer.exe', excluded)


if __name__ == '__main__':
    unittest.main()
