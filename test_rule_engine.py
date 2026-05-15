import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voice_agent'))

print("=" * 80)
print("规则引擎测试 - 确保信息提取不失败")
print("=" * 80)
print()

from voice_agent.services.rule_engine import rule_based_extract, extract_plate_number, extract_phone_number, extract_company, extract_purpose

test_cases = [
    {"input": "浙AMS999", "expected_plate": "浙AMS999"},
    {"input": "车牌是沪A12345", "expected_plate": "沪A12345"},
    {"input": "我的车牌粤B888888", "expected_plate": "粤B888888"},
    {"input": "露帕股份有限公司", "expected_company": "露帕股份有限公司"},
    {"input": "我来蓝色鲸鱼科技送货", "expected_company": "蓝色鲸鱼科技", "expected_purpose": "送货"},
    {"input": "18620250703", "expected_phone": "18620250703"},
    {"input": "电话是13812345678", "expected_phone": "13812345678"},
    {"input": "来做技术支持", "expected_purpose": "技术支持"},
    {"input": "我来开会的", "expected_purpose": "开会"},
    {"input": "浙AMS999 露帕股份 技术测试", "expected_plate": "浙AMS999", "expected_company": "露帕股份"}
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

print("\n" + "="*80)
print("规则引擎测试完成！")
print("="*80)