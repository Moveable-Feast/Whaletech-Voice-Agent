import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 80)
print("规则引擎增强测试 - 上海宝钢场景")
print("=" * 80)
print()

from voice_agent.services.rule_engine import rule_based_extract, extract_company, extract_purpose, extract_plate_number, extract_phone_number

test_cases = [
    {"input": "我是去上海宝钢", "expected_company": "上海宝钢"},
    {"input": "去上海宝钢", "expected_company": "上海宝钢"},
    {"input": "上海宝钢有限公司", "expected_company": "上海宝钢有限公司"},
    {"input": "苏A12345", "expected_plate": "苏A12345"},
    {"input": "我是来送货的", "expected_purpose": "送货"},
    {"input": "送货", "expected_purpose": "送货"},
    {"input": "13011111111", "expected_phone": "13011111111"},
    {"input": "上海宝钢有限公司，苏A12345", "expected_company": "上海宝钢有限公司", "expected_plate": "苏A12345"},
    {"input": "我是去蓝色鲸鱼科技送货", "expected_company": "蓝色鲸鱼科技", "expected_purpose": "送货"},
    {"input": "露帕股份技术测试", "expected_company": "露帕股份", "expected_purpose": "测试"}
]

print("【规则引擎提取测试】")
print("-" * 50)

for i, test in enumerate(test_cases, 1):
    result = rule_based_extract(test["input"])
    print(f"\n测试 {i}: {test['input']}")
    print(f"提取结果: {result}")
    
    success = True
    if "expected_plate" in test and result['plate_number'] != test['expected_plate']:
        print(f"  ❌ 车牌提取失败: 期望={test['expected_plate']}, 实际={result['plate_number']}")
        success = False
    else:
        print(f"  ✅ 车牌: {result['plate_number']}")
    
    if "expected_company" in test and result['company'] != test['expected_company']:
        print(f"  ❌ 公司提取失败: 期望={test['expected_company']}, 实际={result['company']}")
        success = False
    else:
        print(f"  ✅ 公司: {result['company']}")
    
    if "expected_phone" in test and result['phone'] != test['expected_phone']:
        print(f"  ❌ 电话提取失败: 期望={test['expected_phone']}, 实际={result['phone']}")
        success = False
    else:
        print(f"  ✅ 电话: {result['phone']}")
    
    if "expected_purpose" in test and result['purpose'] != test['expected_purpose']:
        print(f"  ❌ 事由提取失败: 期望={test['expected_purpose']}, 实际={result['purpose']}")
        success = False
    else:
        print(f"  ✅ 事由: {result['purpose']}")

print("\n【完整对话场景测试】")
print("-" * 50)

conversation = [
    {"input": "你好，我是来送货的", "expected_purpose": "送货"},
    {"input": "我是去上海宝钢", "expected_company": "上海宝钢"},
    {"input": "上海宝钢有限公司，苏A12345", "expected_company": "上海宝钢有限公司", "expected_plate": "苏A12345"},
    {"input": "13011111111", "expected_phone": "13011111111"}
]

state = {'plate_number': '', 'company': '', 'phone': '', 'purpose': ''}

for i, step in enumerate(conversation, 1):
    print(f"\n第 {i} 轮: {step['input']}")
    
    result = rule_based_extract(step['input'])
    
    if result['plate_number'] and not state['plate_number']:
        state['plate_number'] = result['plate_number']
    if result['company'] and not state['company']:
        state['company'] = result['company']
    if result['phone'] and not state['phone']:
        state['phone'] = result['phone']
    if result['purpose'] and not state['purpose']:
        state['purpose'] = result['purpose']
    
    print(f"当前状态: {state}")

print("\n最终登记信息:")
print(f"  车牌号: {state['plate_number']}")
print(f"  公司: {state['company']}")
print(f"  电话: {state['phone']}")
print(f"  事由: {state['purpose']}")

print("\n" + "="*80)
print("测试完成！")
print("="*80)