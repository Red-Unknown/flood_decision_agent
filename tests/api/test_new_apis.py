"""
测试新实现的API
- GET /api/conversations/{id}/plans
- GET /api/conversations/{id}/specs
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from web.backend.main import app

client = TestClient(app)


def test_get_plans_api():
    """测试获取规划列表API"""
    print("\n=== 测试 GET /api/conversations/{id}/plans ===")
    
    # 1. 创建对话
    response = client.post("/api/conversations", json={"title": "Plan测试对话"})
    assert response.status_code == 200
    conv_id = response.json()["id"]
    print(f"[PASS] 创建对话: {conv_id}")
    
    # 2. 创建几个规划
    plan_ids = []
    for i in range(3):
        plan_id = f"plan_test_{i+1}"
        response = client.post(f"/api/plans/{plan_id}/generate", json={
            "user_input": f"测试规划 {i+1}"
        })
        assert response.status_code == 200
        plan_ids.append(plan_id)
    print(f"[PASS] 创建 {len(plan_ids)} 个规划")
    
    # 3. 获取规划列表
    response = client.get(f"/api/conversations/{conv_id}/plans")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data
    print(f"[PASS] 获取规划列表: 共 {len(data['data'])} 个规划")
    
    # 4. 测试状态过滤
    response = client.get(f"/api/conversations/{conv_id}/plans?status=draft")
    assert response.status_code == 200
    data = response.json()
    print(f"[PASS] 状态过滤(draft): {len(data['data'])} 个规划")
    
    # 5. 测试分页
    response = client.get(f"/api/conversations/{conv_id}/plans?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page_size"] == 2
    print(f"[PASS] 分页: page=1, page_size=2")
    
    # 6. 测试不存在的对话
    response = client.get("/api/conversations/non_existent/plans")
    assert response.status_code == 404
    print("[PASS] 不存在的对话返回404")
    
    # 清理
    client.delete(f"/api/conversations/{conv_id}")
    print("[PASS] 清理完成")


def test_get_specs_api():
    """测试获取规格列表API"""
    print("\n=== 测试 GET /api/conversations/{id}/specs ===")
    
    # 1. 创建对话
    response = client.post("/api/conversations", json={"title": "Spec测试对话"})
    assert response.status_code == 200
    conv_id = response.json()["id"]
    print(f"[PASS] 创建对话: {conv_id}")
    
    # 2. 创建几个规格
    spec_names = []
    for i in range(3):
        feature_name = f"test-spec-{i+1}"
        response = client.post(f"/api/specs/{feature_name}/generate", json={
            "user_input": f"测试规格 {i+1}"
        })
        assert response.status_code == 200
        spec_names.append(feature_name)
    print(f"[PASS] 创建 {len(spec_names)} 个规格")
    
    # 3. 获取规格列表
    response = client.get(f"/api/conversations/{conv_id}/specs")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "pagination" in data
    print(f"[PASS] 获取规格列表: 共 {len(data['data'])} 个规格")
    
    # 4. 测试状态过滤
    response = client.get(f"/api/conversations/{conv_id}/specs?status=draft")
    assert response.status_code == 200
    data = response.json()
    print(f"[PASS] 状态过滤(draft): {len(data['data'])} 个规格")
    
    # 5. 测试分页
    response = client.get(f"/api/conversations/{conv_id}/specs?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page_size"] == 2
    print(f"[PASS] 分页: page=1, page_size=2")
    
    # 6. 测试不存在的对话
    response = client.get("/api/conversations/non_existent/specs")
    assert response.status_code == 404
    print("[PASS] 不存在的对话返回404")
    
    # 清理
    client.delete(f"/api/conversations/{conv_id}")
    print("[PASS] 清理完成")


def test_response_structure():
    """测试响应结构"""
    print("\n=== 测试响应结构 ===")
    
    # 创建对话和规划
    response = client.post("/api/conversations", json={"title": "结构测试"})
    conv_id = response.json()["id"]
    
    client.post("/api/plans/plan_struct_test/generate", json={"user_input": "测试"})
    
    # 获取规划列表并检查结构
    response = client.get(f"/api/conversations/{conv_id}/plans")
    data = response.json()
    
    # 检查顶层结构
    assert "success" in data
    assert "data" in data
    assert "pagination" in data
    print("[PASS] 规划列表响应结构正确")
    
    # 检查分页结构
    pagination = data["pagination"]
    assert "page" in pagination
    assert "page_size" in pagination
    assert "total" in pagination
    assert "total_pages" in pagination
    print("[PASS] 分页信息结构正确")
    
    # 检查规划项结构
    if data["data"]:
        plan = data["data"][0]
        assert "plan_id" in plan
        assert "title" in plan
        assert "status" in plan
        assert "version" in plan
        assert "created_at" in plan
        assert "updated_at" in plan
        print("[PASS] 规划项结构正确")
    
    # 创建规格并检查结构
    client.post("/api/specs/spec_struct_test/generate", json={"user_input": "测试"})
    
    response = client.get(f"/api/conversations/{conv_id}/specs")
    data = response.json()
    
    if data["data"]:
        spec = data["data"][0]
        assert "spec_id" in spec
        assert "feature_name" in spec
        assert "display_name" in spec
        assert "status" in spec
        assert "version" in spec
        assert "created_at" in spec
        assert "updated_at" in spec
        print("[PASS] 规格项结构正确")
    
    # 清理
    client.delete(f"/api/conversations/{conv_id}")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试新API")
    print("=" * 60)
    
    try:
        test_get_plans_api()
        test_get_specs_api()
        test_response_structure()
        
        print("\n" + "=" * 60)
        print("所有测试通过!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
