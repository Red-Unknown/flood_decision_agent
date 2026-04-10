# -*- coding: utf-8 -*-
"""安全地修复导入路径"""

import os
import re

def fix_imports(file_path):
    """修复文件中的导入"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False
    
    original = content
    
    # 替换导入路径
    content = content.replace(
        'flood_decision_agent.infra.logging',
        'flood_decision_agent.infrastructure.logging'
    )
    content = content.replace(
        'flood_decision_agent.infra.kimi_guard',
        'flood_decision_agent.infrastructure.llm.guards.kimi_guard'
    )
    
    if content != original:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except:
            return False
    return False

def main():
    count = 0
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                if fix_imports(path):
                    print(f'Fixed: {path}')
                    count += 1
    print(f'\nTotal files fixed: {count}')

if __name__ == '__main__':
    main()
