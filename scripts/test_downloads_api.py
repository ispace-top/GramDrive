import httpx
import json
import os
import uuid

# --- 配置 ---
# 如果您的应用运行在不同的地址或端口，请修改这里
BASE_URL = os.getenv("TGSTATE_BASE_URL", "http://127.0.0.1:8000")
# 如果您的应用设置了密码，请先登录并在下方填入有效的 session_id cookie
# 获取方法：浏览器登录后，在开发者工具(F12) -> Application -> Cookies 中找到 `tgstate_session`
SESSION_ID = "" 

# --- 测试脚本 ---

def print_check(text, success=True):
    """打印带状态标记的文本"""
    symbol = "✅" if success else "❌"
    print(f"{symbol} {text}")

def run_test():
    """执行API测试"""
    print(f"--- 开始测试 Downloads API: {BASE_URL} ---
")

    cookies = {}
    if SESSION_ID:
        cookies = {"tgstate_session": SESSION_ID}
        print("使用 Session ID 进行认证。")
    else:
        print("未提供 Session ID，将以匿名方式访问。")
        print("如果您的应用需要密码保护，请设置 SESSION_ID 变量。
")

    try:
        with httpx.Client(base_url=BASE_URL, cookies=cookies, timeout=10.0) as client:
            
            # 1. 测试 GET /api/downloads/config
            print("\n--- 测试 1: GET /api/downloads/config ---")
            original_config = None
            try:
                response = client.get("/api/downloads/config")
                response.raise_for_status()
                print_check("请求成功")
                data = response.json()
                assert data["status"] == "success"
                print_check("响应 status 正确")
                assert "data" in data
                original_config = data["data"]
                print("当前配置:", original_config)
            except Exception as e:
                print_check(f"测试失败: {e}", success=False)
                return # 后续测试依赖此步骤

            # 2. 测试 POST /api/downloads/config
            print("\n--- 测试 2: POST /api/downloads/config ---")
            try:
                # 修改一个值并保存
                new_dir = f"/test/downloads_{uuid.uuid4().hex[:6]}"
                payload = original_config.copy()
                payload["download_dir"] = new_dir
                
                response = client.post("/api/downloads/config", json=payload)
                response.raise_for_status()
                data = response.json()
                assert data["status"] == "success"
                print_check("保存新配置成功")

                # 验证修改是否生效
                response = client.get("/api/downloads/config")
                response.raise_for_status()
                updated_config = response.json()["data"]
                assert updated_config["download_dir"] == new_dir
                print_check("验证配置修改成功")

                # 恢复原始配置
                response = client.post("/api/downloads/config", json=original_config)
                response.raise_for_status()
                assert response.json()["status"] == "success"
                print_check("恢复原始配置成功")

            except Exception as e:
                print_check(f"测试失败: {e}", success=False)

            # 3. 测试 GET /api/downloads/stats
            print("\n--- 测试 3: GET /api/downloads/stats ---")
            try:
                response = client.get("/api/downloads/stats")
                response.raise_for_status()
                data = response.json()
                assert data["status"] == "success"
                print_check("请求成功")
                
                stats_keys = ["total_count", "total_size", "exists_count", "missing_count"]
                for key in stats_keys:
                    assert key in data["data"]
                print_check("统计数据包含所有必需字段")
                print("统计数据:", data["data"])

            except Exception as e:
                print_check(f"测试失败: {e}", success=False)

            # 4. 测试 GET /api/downloads/local-files
            print("\n--- 测试 4: GET /api/downloads/local-files ---")
            try:
                response = client.get("/api/downloads/local-files")
                response.raise_for_status()
                data = response.json()
                assert data["status"] == "success"
                print_check("请求成功")
                
                if isinstance(data["data"], list):
                    print_check("返回数据是列表")
                    print(f"找到 {len(data['data'])} 个本地文件记录。")
                else:
                    print_check("返回数据格式不正确，应为列表。", success=False)
            
            except Exception as e:
                print_check(f"测试失败: {e}", success=False)
            
            print("\n--- 所有可自动执行的测试已完成 ---")
            print("注意: DELETE /api/downloads/local-file 是破坏性操作，未自动测试。")

    except httpx.RequestError as e:
        print_check(f"请求失败: {e}", success=False)
        print("请确保您的 tgState 应用正在运行，并且 BASE_URL 配置正确。")
    except Exception as e:
        print_check(f"测试脚本出现意外错误: {e}", success=False)


if __name__ == "__main__":
    run_test()
