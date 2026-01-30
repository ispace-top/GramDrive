#!/usr/bin/env python3
"""
重置数据库配置的脚本
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import reset_app_settings_in_db, get_app_settings_from_db

print("=== 重置数据库配置 ===")

print("\n当前数据库中的设置:")
current_settings = get_app_settings_from_db()
if current_settings:
    for key, value in current_settings.items():
        if key == "PASS_WORD":
            masked_value = "***" if value else ""
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
else:
    print("  (数据库中无设置)")

print("\n正在重置配置...")
try:
    reset_app_settings_in_db()
    print("✅ 配置已重置")
except Exception as e:
    print(f"❌ 重置失败: {e}")

print("\n重置后的数据库设置:")
new_settings = get_app_settings_from_db()
if new_settings:
    for key, value in new_settings.items():
        if key == "PASS_WORD":
            masked_value = "***" if value else ""
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
else:
    print("  (数据库中无设置)")

print("\n=== 重置完成 ===")