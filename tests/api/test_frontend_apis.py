"""
测试前端需要的API
- 会话管理API
- Spec文件分片获取API
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from web.backend.main import app

client = TestClient(app)


def test_session_apis():
    """测试会话管理API"""
    print("\n=== 测试会话管理API ===")
    
    # 1. 创建会话
    response = client.post("/api/sessions", json={
        "conversation_id": "test_conv_001",
        "mode": "plan"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    session_id = data["session_id"]
    print(f"[PASS] 创建会话: {session_id}")
    
    # 2. 获取会话状态
    response = client.get(f"/api/sessions/{session_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "idle"
    print(f"[PASS] 获取会话状态: {data['status']}")
    
    # 3. 更新会话状态
    response = client.post(f"/api/sessions/{session_id}/update", json={
        "status": "awaiting_confirmation",
        "can_resume": True,
        "current_document": {
            "type": "plan",
            "id": "plan_001",
            "title": "测试规划",
            "status": "draft"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "awaiting_confirmation"
    assert data["can_resume"] is True
    print(f"[PASS] 更新会话状态")
    
    # 4. 恢复会话（新接口）
    response = client.post(f"/api/sessions/{session_id}/resume")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "resumed_from" in data
    print(f"[PASS] 恢复会话（新接口）")
    
    # 5. 恢复会话（兼容旧接口）
    response = client.post("/api/sessions/resume", json={
        "session_id": session_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"[PASS] 恢复会话（兼容旧接口 /api/sessions/resume）")
    
    # 6. 获取不存在的会话
    response = client.get("/api/sessions/non_existent/status")
    assert response.status_code == 404
    print(f"[PASS] 获取不存在会话返回404")
    
    # 7. 列出所有会话
    response = client.get("/api/sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    print(f"[PASS] 列出会话: 共 {len(sessions)} 个")
    
    # 8. 删除会话
    response = client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    print(f"[PASS] 删除会话")


def test_spec_file_apis():
    """测试Spec文件分片获取API"""
    print("\n=== 测试Spec文件分片获取API ===")
    
    # 1. 创建规格
    response = client.post("/api/specs", json={
        "user_input": "测试规格"
    })
    assert response.status_code == 200
    data = response.json()
    feature_name = data["feature_name"]
    print(f"[PASS] 创建规格: {feature_name}")
    
    # 2. 获取规格列表
    response = client.get("/api/specs")
    assert response.status_code == 200
    specs = response.json()
    assert isinstance(specs, list)
    print(f"[PASS] 获取规格列表: 共 {len(specs)} 个")
    
    # 3. 获取规格详情
    response = client.get(f"/api/specs/{feature_name}")
    assert response.status_code == 200
    data = response.json()
    assert data["feature_name"] == feature_name
    assert "files" in data
    print(f"[PASS] 获取规格详情")
    
    # 4. 获取规格文件列表
    response = client.get(f"/api/specs/{feature_name}/files")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "files" in data
    print(f"[PASS] 获取文件列表: {len(data['files'])} 个文件")
    
    # 5. 获取单个文件内容（spec）
    response = client.get(f"/api/specs/{feature_name}/spec")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content" in data
    print(f"[PASS] 获取单个文件内容 (spec)")
    
    # 6. 获取单个文件内容（带.md后缀）
    response = client.get(f"/api/specs/{feature_name}/spec.md")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"[PASS] 获取单个文件内容 (spec.md)")
    
    # 7. 更新文件内容
    response = client.put(f"/api/specs/{feature_name}/spec.md", json={
        "content": "# 更新后的规格内容\n\n这是更新后的内容。"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"[PASS] 更新文件内容")
    
    # 8. 审批规格
    response = client.post(f"/api/specs/{feature_name}/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    print(f"[PASS] 审批规格")


def test_mode_api():
    """测试模式检测API（确认前端调用兼容）"""
    print("\n=== 测试模式检测API ===")
    
    response = client.post("/api/mode/detect", json={
        "user_input": "制定一个洪水预警计划"
    })
    assert response.status_code == 200
    data = response.json()
    assert "recommended_mode" in data
    assert data["recommended_mode"] == "plan"
    print(f"[PASS] 模式检测: {data['recommended_mode']}")


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试前端需要的API")
    print("=" * 60)
    
    try:
        test_session_apis()
        test_spec_file_apis()
        test_mode_api()
        
        print("\n" + "=" * 60)
        print("所有测试通过!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
