#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code Scanner and ADB Launcher
扫描屏幕中间的二维码并通过adb启动小红书应用
"""

import cv2
import numpy as np
import subprocess
import sys
from PIL import ImageGrab
from pyzbar import pyzbar
import re
import time

class QRScanner:
    def __init__(self):
        self.adb_package = "com.xingin.xhs"
    
    def capture_screen_center(self, size=800):
        """
        截取屏幕中心区域
        Args:
            size: 截取区域的大小 (默认400x400像素)
        Returns:
            PIL Image对象
        """
        # 获取屏幕尺寸
        screen = ImageGrab.grab()
        screen_width, screen_height = screen.size
        
        # 计算中心区域坐标
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        left = center_x - size // 2
        top = center_y - size // 2
        right = center_x + size // 2
        bottom = center_y + size // 2
        
        # 截取中心区域
        center_region = screen.crop((left, top, right, bottom))
        return center_region
    
    def scan_qr_code(self, image):
        """
        扫描图像中的二维码
        Args:
            image: PIL Image对象
        Returns:
            二维码内容字符串，如果没有找到返回None
        """
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 转换为灰度图像以提高识别率
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 使用pyzbar解码二维码
        decoded_objects = pyzbar.decode(gray)
        
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            print(f"发现二维码: {qr_data}")
            return qr_data
        
        return None
    
    def validate_xhs_url(self, url):
        """
        验证是否为小红书链接
        Args:
            url: 链接字符串
        Returns:
            布尔值，True表示是有效的小红书链接
        """
        xhs_patterns = [
            r'^xhsdiscover://.*',
            r'^https?://.*xiaohongshu\.com.*',
            r'^https?://.*xhslink\.com.*'
        ]
        
        for pattern in xhs_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def execute_adb_command(self, url):
        """
        执行adb命令启动小红书应用
        Args:
            url: 要打开的链接
        Returns:
            命令执行结果
        """
        try:
            # 构建adb命令
            adb_cmd = [
                'adb', 'shell', 'am', 'start',
                '-a', 'android.intent.action.VIEW',
                '-d', url,
                self.adb_package
            ]
            
            print(f"执行命令: {' '.join(adb_cmd)}")
            
            # 执行命令
            result = subprocess.run(
                adb_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ ADB命令执行成功!")
                print(f"输出: {result.stdout}")
                return True
            else:
                print("❌ ADB命令执行失败!")
                print(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ ADB命令执行超时!")
            return False
        except FileNotFoundError:
            print("❌ 找不到adb命令，请确保adb已安装并添加到PATH环境变量中!")
            return False
        except Exception as e:
            print(f"❌ 执行ADB命令时发生错误: {e}")
            return False
    
    def click_coordinate(self, x, y, delay=2):
        """
        等待指定时间后点击手机屏幕上的指定坐标
        Args:
            x: X坐标
            y: Y坐标  
            delay: 等待时间（秒）
        Returns:
            布尔值，True表示点击成功
        """
        try:
            print(f"⏱️  等待 {delay} 秒...")
            time.sleep(delay)
            
            # 构建adb点击命令
            tap_cmd = [
                'adb', 'shell', 'input', 'tap',
                str(x), str(y)
            ]
            
            print(f"执行点击命令: {' '.join(tap_cmd)}")
            
            # 执行点击命令
            result = subprocess.run(
                tap_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ 成功点击坐标 ({x}, {y})!")
                return True
            else:
                print(f"❌ 点击坐标失败!")
                print(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 点击命令执行超时!")
            return False
        except Exception as e:
            print(f"❌ 执行点击命令时发生错误: {e}")
            return False
    
    def check_adb_connection(self):
        """
        检查ADB连接状态
        Returns:
            布尔值，True表示有设备连接
        """
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                devices = [line for line in lines[1:] if line.strip() and 'device' in line]
                
                if devices:
                    print(f"✅ 发现 {len(devices)} 个连接的设备:")
                    for device in devices:
                        print(f"  - {device}")
                    return True
                else:
                    print("❌ 没有发现连接的设备")
                    return False
            else:
                print(f"❌ ADB命令执行失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 检查ADB连接时发生错误: {e}")
            return False
    
    def run(self, max_attempts=10, delay=3):
        """
        主运行函数
        Args:
            max_attempts: 最大尝试次数
            delay: 每次尝试间隔秒数
        """
        print("🚀 启动QR码扫描器...")
        print("=" * 50)
        
        # 检查ADB连接
        if not self.check_adb_connection():
            print("请确保:")
            print("1. 手机已通过USB连接到电脑")
            print("2. 手机已开启USB调试模式")
            print("3. 已授权电脑进行USB调试")
            return False
        
        print(f"\n📱 开始扫描屏幕中心区域的二维码...")
        print(f"最大尝试次数: {max_attempts}, 间隔: {delay}秒")
        print("请确保二维码位于屏幕中央区域")
        print("-" * 50)
        
        for attempt in range(1, max_attempts + 1):
            print(f"\n🔍 第 {attempt} 次尝试扫描...")
            
            try:
                # 截取屏幕中心
                center_image = self.capture_screen_center()
                
                # 扫描二维码
                qr_content = self.scan_qr_code(center_image)
                
                if qr_content:
                    if self.validate_xhs_url(qr_content):
                        print(f"✅ 发现有效的小红书链接: {qr_content}")
                        
                        # 执行ADB命令
                        if self.execute_adb_command(qr_content):
                            # 等待2秒后点击坐标
                            if self.click_coordinate(800, 2210): # 收藏按钮代表的坐标
                                print("\n🎉 任务完成!")
                                return True
                            else:
                                print("\n⚠️ ADB命令执行成功，但点击坐标失败")
                                return True  # 主要任务已完成，点击失败不影响整体结果
                        else:
                            print("\n❌ ADB命令执行失败，但二维码扫描成功")
                            return False
                    else:
                        print(f"⚠️  发现二维码但不是小红书链接: {qr_content}")
                else:
                    print("❌ 未发现二维码")
                
            except Exception as e:
                print(f"❌ 扫描过程中发生错误: {e}")
            
            if attempt < max_attempts:
                print(f"⏱️  等待 {delay} 秒后重试...")
                time.sleep(delay)
        
        print(f"\n❌ 经过 {max_attempts} 次尝试，未能成功扫描到有效的小红书二维码")
        return False

def main():
    """主函数"""
    print("小红书二维码扫描器 v1.0")
    print("=" * 50)
    
    # 检查依赖
    try:
        import cv2
        import pyzbar
        from PIL import ImageGrab
    except ImportError as e:
        print(f"❌ 缺少必要的依赖库: {e}")
        print("\n请安装以下依赖:")
        print("pip install opencv-python pillow pyzbar")
        print("\n注意: pyzbar可能需要额外的系统依赖")
        print("Windows: 通常随pip自动安装")
        print("Linux: sudo apt-get install libzbar0")
        print("macOS: brew install zbar")
        return
    
    # 创建扫描器实例
    scanner = QRScanner()
    
    # 运行扫描
    try:
        scanner.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序运行时发生未知错误: {e}")

if __name__ == "__main__":
    main()
