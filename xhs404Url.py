#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书404链接处理工具
从小红书网页链接中提取ID，转换为APP深度链接，并通过ADB打开
"""


# 终端输入一些链接，每行一个，这样的
# https://www.xiaohongshu.com/explore/652b91f0000000001f03b570?xsec_token=.....=&xsec_source=pc_search&source=unknown
# 从中提取出来这一部分  652b91f0000000001f03b570
# 然后将652b91f0000000001f03b570变为xhsdiscover://item/652b91f0000000001f03b570?source=pcweb_access_limit
# 然后把这个链接作为execute_adb_command(url)的参数执行


import subprocess
import re
import time
import sys


class XhsUrlProcessor:
    """小红书URL处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.adb_package = "com.xingin.xhs"  # 小红书包名
        
    def extract_id_from_url(self, url):
        """
        从小红书URL中提取ID
        Args:
            url: 小红书网页链接
        Returns:
            提取到的ID，如果提取失败返回None
        """
        try:
            # 匹配模式：/explore/后面跟着的ID
            pattern = r'/explore/([a-f0-9]{24})'
            match = re.search(pattern, url)
            
            if match:
                return match.group(1)
            else:
                print(f"❌ 无法从URL中提取ID: {url}")
                return None
                
        except Exception as e:
            print(f"❌ 提取ID时发生错误: {e}")
            return None
    
    def convert_to_app_url(self, item_id):
        """
        将ID转换为小红书APP深度链接
        Args:
            item_id: 小红书内容ID
        Returns:
            转换后的APP深度链接
        """
        return f"xhsdiscover://item/{item_id}?source=pcweb_access_limit"
    
    def click_coordinate(self, x, y):
        """
        点击指定坐标
        Args:
            x: X坐标
            y: Y坐标
        Returns:
            点击是否成功
        """
        try:
            # 等待2秒让页面加载
            time.sleep(2)
            
            # 执行点击命令
            click_cmd = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
            print(f"点击坐标: ({x}, {y})")
            
            result = subprocess.run(
                click_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ 点击成功!")
                return True
            else:
                print(f"❌ 点击失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 点击坐标时发生错误: {e}")
            return False
    
    def process_single_url(self, url):
        """
        处理单个URL
        Args:
            url: 要处理的URL
        Returns:
            处理是否成功
        """
        print(f"\n📱 处理URL: {url}")
        
        # 提取ID
        item_id = self.extract_id_from_url(url.strip())
        if not item_id:
            return False
            
        print(f"📋 提取到ID: {item_id}")
        
        # 转换为APP链接
        app_url = self.convert_to_app_url(item_id)
        print(f"🔗 转换后的链接: {app_url}")
        
        # 执行ADB命令
        if self.execute_adb_command(app_url):
            # 等待2秒后点击坐标
            if self.click_coordinate(865, 2690):  # 收藏按钮坐标
                print("\n🎉 任务完成!")
                return True
            else:
                print("\n⚠️ ADB命令执行成功，但点击坐标失败")
                return True  # 主要任务已完成，点击失败不影响整体结果
        else:
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
    
    def check_adb_connection(self):
        """
        检查ADB连接状态
        Returns:
            连接是否正常
        """
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                connected_devices = [line for line in devices if line.strip() and 'device' in line]
                
                if connected_devices:
                    print(f"✅ 检测到 {len(connected_devices)} 个设备连接")
                    for device in connected_devices:
                        print(f"   📱 {device}")
                    return True
                else:
                    print("❌ 没有检测到连接的设备")
                    print("请确保:")
                    print("  1. 设备已连接并开启USB调试")
                    print("  2. 已授权ADB调试")
                    return False
            else:
                print("❌ ADB命令执行失败")
                return False
                
        except FileNotFoundError:
            print("❌ 找不到adb命令，请确保adb已安装并添加到PATH环境变量中!")
            return False
        except Exception as e:
            print(f"❌ 检查ADB连接时发生错误: {e}")
            return False
    
    def process_urls_from_input(self):
        """
        从用户输入处理多个URL
        """
        print("🔗 小红书404链接处理工具")
        print("=" * 50)
        print("请输入小红书链接，每行一个，输入空行结束:")
        print("示例: https://www.xiaohongshu.com/explore/652b91f0000000001f03b570?...")
        print()
        
        # 检查ADB连接
        if not self.check_adb_connection():
            return
        
        urls = []
        while True:
            try:
                line = input("🔗 输入链接: ").strip()
                if not line:
                    break
                urls.append(line)
            except KeyboardInterrupt:
                print("\n\n👋 用户取消操作")
                return
            except EOFError:
                break
        
        if not urls:
            print("❌ 没有输入任何链接")
            return
        
        print(f"\n📋 共收到 {len(urls)} 个链接，开始处理...")
        
        success_count = 0
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*20} 处理第 {i}/{len(urls)} 个链接 {'='*20}")
            
            if self.process_single_url(url):
                success_count += 1
                
            # 如果不是最后一个链接，询问是否继续
            if i < len(urls):
                try:
                    continue_choice = input("\n⏳ 按回车继续下一个，输入'q'退出: ").strip().lower()
                    if continue_choice == 'q':
                        break
                except KeyboardInterrupt:
                    print("\n\n👋 用户取消操作")
                    break
        
        print(f"\n🎯 处理完成! 成功: {success_count}/{len(urls)}")
    
    def process_urls_from_file(self, file_path):
        """
        从文件读取URL并处理
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print("❌ 文件中没有找到任何链接")
                return
            
            print(f"📁 从文件读取到 {len(urls)} 个链接")
            
            # 检查ADB连接
            if not self.check_adb_connection():
                return
            
            success_count = 0
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*20} 处理第 {i}/{len(urls)} 个链接 {'='*20}")
                
                if self.process_single_url(url):
                    success_count += 1
                
                # 添加延迟避免过快操作
                if i < len(urls):
                    time.sleep(1)
            
            print(f"\n🎯 处理完成! 成功: {success_count}/{len(urls)}")
            
        except FileNotFoundError:
            print(f"❌ 找不到文件: {file_path}")
        except Exception as e:
            print(f"❌ 读取文件时发生错误: {e}")


def main():
    """主程序入口"""
    processor = XhsUrlProcessor()
    
    if len(sys.argv) > 1:
        # 从文件读取
        file_path = sys.argv[1]
        processor.process_urls_from_file(file_path)
    else:
        # 从用户输入读取
        processor.process_urls_from_input()


if __name__ == "__main__":
    main()