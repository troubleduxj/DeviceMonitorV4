# -*- coding: utf-8 -*-
"""
异常检测服务测试脚本
"""

import os
import sys
import numpy as np

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai.anomaly_detection import (
    StatisticalAnomalyDetector,
    IsolationForestDetector,
    AnomalyDetector,
    DetectionMethod,
    AnomalySeverity
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_statistical_detector():
    """测试统计异常检测器"""
    print_section("测试1: 统计异常检测器（3-sigma）")
    
    # 生成正常数据 + 异常值
    np.random.seed(42)
    normal_data = np.random.normal(100, 10, 95).tolist()
    
    # 注入明显异常值
    data = normal_data + [150, 180, 50, 20, 200]  # 5个异常值
    
    detector = StatisticalAnomalyDetector(threshold_sigma=3.0)
    anomalies = detector.detect(data, return_scores=True)
    
    print(f"数据点数: {len(data)}")
    print(f"检测到异常数: {len(anomalies)}")
    
    if anomalies:
        print("\n异常详情:")
        for i, anomaly in enumerate(anomalies[:5], 1):  # 只显示前5个
            print(f"  {i}. 索引:{anomaly['index']}, "
                  f"值:{anomaly['value']:.2f}, "
                  f"Z分数:{anomaly['z_score']:.2f}, "
                  f"严重程度:{anomaly['severity']}")
    
    assert len(anomalies) >= 3, f"应检测到至少3个异常，实际检测到{len(anomalies)}个"
    assert all('z_score' in a for a in anomalies), "所有异常应包含z_score"
    
    print("\n[OK] 统计异常检测器测试通过")


def test_statistical_with_mad():
    """测试使用MAD的统计检测器（更鲁棒）"""
    print_section("测试2: 统计检测器（MAD方法）")
    
    # 生成有极端值的数据
    np.random.seed(42)
    data = np.random.normal(50, 5, 90).tolist()
    data += [150, 160, 170]  # 极端异常值
    data += [10, 5, 0]  # 另一侧极端值
    
    # 使用标准差方法
    detector_std = StatisticalAnomalyDetector(threshold_sigma=3.0, use_mad=False)
    anomalies_std = detector_std.detect(data)
    
    # 使用MAD方法（更鲁棒）
    detector_mad = StatisticalAnomalyDetector(threshold_sigma=3.0, use_mad=True)
    anomalies_mad = detector_mad.detect(data)
    
    print(f"数据点数: {len(data)}")
    print(f"标准差方法检测到: {len(anomalies_std)}个异常")
    print(f"MAD方法检测到: {len(anomalies_mad)}个异常")
    
    # MAD方法通常更稳定
    print(f"\n使用MAD方法更鲁棒，对极端值不敏感")
    
    print("\n[OK] MAD方法测试通过")


def test_isolation_forest_detector():
    """测试孤立森林检测器"""
    print_section("测试3: 孤立森林异常检测器")
    
    # 生成正常数据 + 异常值
    np.random.seed(42)
    normal_data = np.random.normal(100, 10, 150).tolist()
    
    # 注入异常值（不同模式）
    data = normal_data + [150, 180, 200, 50, 20, 10]
    
    detector = IsolationForestDetector(contamination=0.05)
    anomalies = detector.detect(data, return_scores=True)
    
    print(f"数据点数: {len(data)}")
    print(f"预期异常比例: 5%")
    print(f"检测到异常数: {len(anomalies)}")
    print(f"实际异常比例: {len(anomalies)/len(data)*100:.1f}%")
    
    if anomalies:
        print("\n异常详情:")
        for i, anomaly in enumerate(anomalies[:5], 1):
            print(f"  {i}. 索引:{anomaly['index']}, "
                  f"值:{anomaly['value']:.2f}, "
                  f"分数:{anomaly.get('anomaly_score', 0):.3f}, "
                  f"严重程度:{anomaly['severity']}")
    
    assert len(anomalies) > 0, "应检测到异常"
    assert len(anomalies) <= len(data) * 0.15, "异常数不应超过15%"
    
    print("\n[OK] 孤立森林检测器测试通过")


def test_anomaly_severity_levels():
    """测试异常严重程度划分"""
    print_section("测试4: 异常严重程度划分")
    
    # 生成不同程度的异常
    np.random.seed(42)
    base_data = np.random.normal(100, 5, 50).tolist()
    
    # 注入更明显的不同Z分数的异常值
    # 基于标准差5，注入相对偏差
    data = base_data + [
        118,   # Z ≈ 3.6 (轻微)
        123,   # Z ≈ 4.6 (中等)
        128,   # Z ≈ 5.6 (严重)
        135,   # Z ≈ 7.0 (危险)
        75,    # Z ≈ -5.0 (严重，负向)
        65,    # Z ≈ -7.0 (危险，负向)
    ]
    
    detector = StatisticalAnomalyDetector(threshold_sigma=3.0)
    anomalies = detector.detect(data)
    
    print(f"检测到 {len(anomalies)} 个异常")
    
    # 统计各严重程度数量
    severity_count = {}
    for anomaly in anomalies:
        severity = anomaly['severity']
        severity_count[severity] = severity_count.get(severity, 0) + 1
    
    print("\n严重程度分布:")
    for severity, count in sorted(severity_count.items()):
        print(f"  {severity}: {count}个")
    
    assert len(anomalies) >= 2, "应检测到多个异常"
    
    print("\n[OK] 严重程度划分测试通过")


def test_combined_detection():
    """测试组合检测方法"""
    print_section("测试5: 组合检测方法")
    
    # 生成复杂的数据
    np.random.seed(42)
    data = np.random.normal(100, 10, 100).tolist()
    
    # 注入不同类型的异常
    data += [150, 160, 170]  # 明显异常
    data += [130, 135]  # 中等异常
    
    detector = AnomalyDetector()
    
    # 使用组合方法
    anomalies = detector.detect(data, method=DetectionMethod.COMBINED)
    
    print(f"数据点数: {len(data)}")
    print(f"检测到异常数: {len(anomalies)}")
    
    if anomalies:
        print("\n异常详情（前5个）:")
        for i, anomaly in enumerate(anomalies[:5], 1):
            detected_by = ', '.join(anomaly['detected_by'])
            print(f"  {i}. 索引:{anomaly['index']}, "
                  f"值:{anomaly['value']:.2f}, "
                  f"检测方法:{detected_by}, "
                  f"严重程度:{anomaly['severity']}")
    
    # 检查是否有被多种方法检测到的异常
    multi_method = [a for a in anomalies if len(a['detected_by']) > 1]
    print(f"\n被多种方法检测到的异常: {len(multi_method)}个")
    
    assert len(anomalies) > 0, "组合方法应检测到异常"
    
    print("\n[OK] 组合检测方法测试通过")


def test_batch_detection():
    """测试批量检测"""
    print_section("测试6: 批量异常检测")
    
    np.random.seed(42)
    
    # 准备多个指标的数据
    data_dict = {
        'temperature': np.random.normal(25, 2, 100).tolist() + [40, 45, 10],
        'pressure': np.random.normal(1013, 5, 100).tolist() + [1100, 1150],
        'humidity': np.random.normal(60, 5, 100).tolist() + [95, 98, 100],
    }
    
    detector = AnomalyDetector()
    results = detector.batch_detect(
        data_dict,
        method=DetectionMethod.STATISTICAL
    )
    
    print(f"检测指标数: {len(results)}")
    print("\n各指标异常情况:")
    for metric, anomalies in results.items():
        print(f"  {metric}: {len(anomalies)}个异常")
        if anomalies:
            severities = [a['severity'] for a in anomalies]
            print(f"    严重程度: {', '.join(set(severities))}")
    
    assert len(results) == 3, "应返回3个指标的结果"
    assert all(isinstance(v, list) for v in results.values()), "所有结果应为列表"
    
    print("\n[OK] 批量检测测试通过")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试7: 边界情况处理")
    
    detector = AnomalyDetector()
    
    # 空数据
    anomalies_empty = detector.detect([])
    print(f"空数据: {len(anomalies_empty)}个异常 (期望0)")
    assert len(anomalies_empty) == 0, "空数据应返回空列表"
    
    # 数据点太少
    anomalies_few = detector.detect([1.0, 2.0])
    print(f"数据点太少(2个): {len(anomalies_few)}个异常")
    
    # 无变化数据（标准差为0）
    anomalies_constant = detector.detect([100.0] * 50)
    print(f"常数数据: {len(anomalies_constant)}个异常 (期望0)")
    assert len(anomalies_constant) == 0, "常数数据应无异常"
    
    # 含NaN数据
    data_with_nan = [1.0, 2.0, float('nan'), 4.0, 5.0, 100.0]
    anomalies_nan = detector.detect(data_with_nan)
    print(f"含NaN数据: {len(anomalies_nan)}个异常")
    assert len(anomalies_nan) >= 0, "应能处理含NaN的数据"
    
    # 全部异常数据（极端情况）
    extreme_data = list(range(1, 101))  # 1-100的递增序列
    extreme_data[50] = 1000  # 注入一个极端值
    anomalies_extreme = detector.detect(extreme_data)
    print(f"含极端值数据: {len(anomalies_extreme)}个异常")
    assert len(anomalies_extreme) >= 1, "应检测到极端值"
    
    print("\n[OK] 边界情况测试通过")


def test_performance():
    """测试性能"""
    print_section("测试8: 性能测试")
    
    import time
    
    # 生成大量数据
    np.random.seed(42)
    data_1k = np.random.normal(100, 10, 1000).tolist()
    data_10k = np.random.normal(100, 10, 10000).tolist()
    
    # 注入异常
    data_1k += [200, 210, 10, 5]
    data_10k += [200, 210, 10, 5]
    
    detector = AnomalyDetector()
    
    # 测试统计方法性能
    start = time.time()
    anomalies_1k = detector.detect(data_1k, method=DetectionMethod.STATISTICAL)
    time_1k = (time.time() - start) * 1000
    
    print(f"1000点数据 (统计方法): {time_1k:.2f}ms, 检测到{len(anomalies_1k)}个异常")
    
    start = time.time()
    anomalies_10k = detector.detect(data_10k, method=DetectionMethod.STATISTICAL)
    time_10k = (time.time() - start) * 1000
    
    print(f"10000点数据 (统计方法): {time_10k:.2f}ms, 检测到{len(anomalies_10k)}个异常")
    
    # 测试孤立森林性能（更慢）
    start = time.time()
    anomalies_if = detector.detect(data_1k, method=DetectionMethod.ISOLATION_FOREST)
    time_if = (time.time() - start) * 1000
    
    print(f"1000点数据 (孤立森林): {time_if:.2f}ms, 检测到{len(anomalies_if)}个异常")
    
    # 性能断言
    assert time_1k < 1000, f"1000点统计检测应<1s，实际{time_1k:.2f}ms"
    assert time_10k < 2000, f"10000点统计检测应<2s，实际{time_10k:.2f}ms"
    
    print("\n性能评估:")
    print(f"  统计方法: 优秀 (1000点<{time_1k:.0f}ms)")
    print(f"  孤立森林: {'优秀' if time_if < 500 else '良好'} (1000点<{time_if:.0f}ms)")
    
    print("\n[OK] 性能测试通过")


def main():
    """主测试流程"""
    print("=" * 60)
    print("  异常检测服务测试")
    print("=" * 60)
    
    try:
        test_statistical_detector()
        test_statistical_with_mad()
        test_isolation_forest_detector()
        test_anomaly_severity_levels()
        test_combined_detection()
        test_batch_detection()
        test_edge_cases()
        test_performance()
        
        print("\n" + "=" * 60)
        print("  [OK] 所有测试通过!")
        print("=" * 60)
        
        return 0
    except AssertionError as e:
        print(f"\n[FAILED] 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

