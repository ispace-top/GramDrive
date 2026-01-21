import httpx
import json
import os

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
    print(f"--- 开始测试 tgState API: {BASE_URL} ---\n")

    cookies = {}
    if SESSION_ID:
        cookies = {"tgstate_session": SESSION_ID}
        print("使用 Session ID 进行认证。")
    else:
        print("未提供 Session ID，将以匿名方式访问。")
        print("如果您的应用需要密码保护，请设置 SESSION_ID 变量。\n")

    try:
        with httpx.Client(base_url=BASE_URL, cookies=cookies, timeout=10.0) as client:
            # 1. 测试 /api/stats/dashboard 端点
            print("--- 测试 1: GET /api/stats/dashboard ---")
            try:
                response = client.get("/api/stats/dashboard")

                if response.status_code == 200:
                    print_check(f"请求成功，状态码: {response.status_code}")
                    data = response.json()

                    # 验证基本结构
                    assert data.get("status") == "success", "响应状态应为 'success'"
                    print_check("响应 'status' 字段正确")
                    
                    assert "data" in data, "响应中应包含 'data' 字段"
                    print_check("响应包含 'data' 字段")

                    stats_data = data["data"]
                    
                    # 验证关键统计字段
                    required_keys = [
                        "total_files", "total_size", "by_type", "recent_uploads", 
                        "top_downloads", "local_files_count", "total_tags", 
                        "total_size_formatted"
                    ]
                    for key in required_keys:
                        assert key in stats_data, f"统计数据中应包含 '{key}'"
                    print_check(f"统计数据包含所有必需字段: {', '.join(required_keys)}")
                    
                    print("\n--- /api/stats/dashboard 测试通过 ---")

                elif response.status_code == 401:
                    print_check("请求被拒绝 (401 Unauthorized)，这是预期的行为，因为需要登录。", success=True)
                    print("请在脚本顶部设置有效的 SESSION_ID 后重试以进行完整测试。" )
                
                else:
                    print_check(f"请求失败，非预期的状态码: {response.status_code}", success=False)
                    try:
                        print("响应内容:", response.json())
                    except json.JSONDecodeError:
                        print("响应内容:", response.text)

            except httpx.RequestError as e:
                print_check(f"请求失败: {e}", success=False)
                print("请确保您的 tgState 应用正在运行，并且 BASE_URL 配置正确。" )

    except Exception as e:
        print_check(f"测试脚本出现意外错误: {e}", success=False)

    print("\n--- 测试结束 ---")


if __name__ == "__main__":
    run_test()
