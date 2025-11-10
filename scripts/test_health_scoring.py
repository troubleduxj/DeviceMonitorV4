# -*- coding: utf-8 -*-
"""
健康评分服务测试脚本
"""

import os
import sys

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai.health_scoring import (
    PerformanceScorer,
    AnomalyScorer,
    TrendScorer,
    UptimeScorer,
    HealthScoreCalculator,
    HealthGrade,
    HealthDimension
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_performance_scorer():
    """测试性能评分器"""
    print_section("测试1: 性能指标评分器")
    
    scorer = PerformanceScorer()
    
    # 测试1: 指标在范围内
    metrics_good = {
        'temperature': 25.0,
        'pressure': 1013.0
    }
    target_ranges = {
        'temperature': (20.0, 30.0),
        'pressure': (1000.0, 1020.0)
    }
    score_good = scorer.score(metrics_good, target_ranges)
    
    print(f"测试场景1: 指标在正常范围内")
    print(f"  指标: {metrics_good}")
    print(f"  目标范围: {target_ranges}")
    print(f"  评分: {score_good:.2f}")
    
    # 测试2: 指标超出范围
    metrics_bad = {
        'temperature': 40.0,  # 超出范围
        'pressure': 950.0     # 低于范围
    }
    score_bad = scorer.score(metrics_bad, target_ranges)
    
    print(f"\n测试场景2: 指标超出范围")
    print(f"  指标: {metrics_bad}")
    print(f"  评分: {score_bad:.2f}")
    
    assert score_good > score_bad, "正常指标评分应高于异常指标"
    assert score_good == 100.0, "完全正常应得满分"
    
    print("\n[OK] 性能评分器测试通过")


def test_anomaly_scorer():
    """测试异常频率评分器"""
    print_section("测试2: 异常频率评分器")
    
    scorer = AnomalyScorer()
    
    # 测试不同异常率
    test_cases = [
        (0, 1000, "无异常"),
        (10, 1000, "1%异常"),
        (50, 1000, "5%异常"),
        (100, 1000, "10%异常"),
        (200, 1000, "20%异常"),
    ]
    
    print("异常率 vs 评分:")
    for anomaly_count, total, desc in test_cases:
        score = scorer.score(anomaly_count, total)
        print(f"  {desc:12s}: {score:6.2f}分 ({anomaly_count}/{total})")
    
    # 验证
    score_0 = scorer.score(0, 1000)
    score_1 = scorer.score(10, 1000)
    score_5 = scorer.score(50, 1000)
    
    assert score_0 > score_1 > score_5, "异常越少，分数应越高"
    assert score_0 == 100.0, "无异常应得满分"
    
    print("\n[OK] 异常频率评分器测试通过")


def test_trend_scorer():
    """测试趋势健康评分器"""
    print_section("测试3: 趋势健康评分器")
    
    scorer = TrendScorer()
    
    # 测试不同趋势
    trends = [
        ("平稳", 0.9, True),
        ("上升", 0.8, True),
        ("下降", 0.8, True),
        ("上升", 0.8, False),  # 上升不好（如温度）
    ]
    
    print("趋势方向 vs 评分:")
    for direction, stability, is_good in trends:
        score = scorer.score(direction, stability, is_good)
        good_desc = "上升好" if is_good else "下降好"
        print(f"  {direction:6s} (稳定性{stability:.1f}, {good_desc}): {score:6.2f}分")
    
    # 验证
    score_stable = scorer.score("平稳", 0.9, True)
    score_up_good = scorer.score("上升", 0.8, True)
    score_up_bad = scorer.score("上升", 0.8, False)
    
    assert score_stable > score_up_good, "平稳通常最优"
    assert score_up_good > score_up_bad, "趋势好坏影响评分"
    
    print("\n[OK] 趋势健康评分器测试通过")


def test_uptime_scorer():
    """测试运行时长评分器"""
    print_section("测试4: 运行时长评分器")
    
    scorer = UptimeScorer()
    
    # 测试不同运行时长
    expected = 720.0  # 30天
    test_cases = [
        (720.0, "100%运行"),
        (684.0, "95%运行"),
        (648.0, "90%运行"),
        (576.0, "80%运行"),
        (360.0, "50%运行"),
        (144.0, "20%运行"),
    ]
    
    print(f"运行时长 vs 评分 (期望{expected}小时):")
    for hours, desc in test_cases:
        score = scorer.score(hours, expected)
        ratio = hours / expected * 100
        print(f"  {desc:12s} ({ratio:5.1f}%): {score:6.2f}分")
    
    # 验证
    score_100 = scorer.score(720, 720)
    score_95 = scorer.score(684, 720)
    score_50 = scorer.score(360, 720)
    
    assert score_100 > score_95 > score_50, "运行时长越长，分数应越高"
    assert score_100 == 100.0, "满运行时长应得满分"
    
    print("\n[OK] 运行时长评分器测试通过")


def test_health_score_calculator():
    """测试健康评分计算器"""
    print_section("测试5: 综合健康评分计算器")
    
    calculator = HealthScoreCalculator()
    
    # 测试场景1: 优秀设备
    result_excellent = calculator.calculate(
        performance_metrics={'temperature': 25.0, 'pressure': 1013.0},
        anomaly_count=5,
        total_count=1000,
        trend_direction="平稳",
        trend_stability=0.9,
        uptime_hours=720.0,
        target_ranges={'temperature': (20, 30), 'pressure': (1000, 1020)}
    )
    
    print("场景1: 优秀设备")
    print(f"  总评分: {result_excellent['total_score']}")
    print(f"  健康等级: {result_excellent['grade']}")
    print(f"  各维度评分:")
    for dim, score in result_excellent['dimension_scores'].items():
        print(f"    {dim:12s}: {score:6.2f}")
    
    # 测试场景2: 较差设备
    result_poor = calculator.calculate(
        performance_metrics={'temperature': 45.0, 'pressure': 900.0},
        anomaly_count=150,
        total_count=1000,
        trend_direction="下降",
        trend_stability=0.5,
        uptime_hours=300.0,
        target_ranges={'temperature': (20, 30), 'pressure': (1000, 1020)}
    )
    
    print("\n场景2: 较差设备")
    print(f"  总评分: {result_poor['total_score']}")
    print(f"  健康等级: {result_poor['grade']}")
    print(f"  各维度评分:")
    for dim, score in result_poor['dimension_scores'].items():
        print(f"    {dim:12s}: {score:6.2f}")
    
    # 验证
    assert result_excellent['total_score'] > result_poor['total_score'], "优秀设备评分应高于较差设备"
    assert 'A-' in result_excellent['grade'] or 'B-' in result_excellent['grade'], "优秀设备应为A或B级"
    assert 'dimension_scores' in result_excellent, "应包含各维度评分"
    
    print("\n[OK] 综合健康评分计算器测试通过")


def test_health_grades():
    """测试健康等级划分"""
    print_section("测试6: 健康等级划分")
    
    calculator = HealthScoreCalculator()
    
    # 构造不同评分场景
    test_scores = [
        (95, "A-优秀"),
        (85, "B-良好"),
        (75, "C-一般"),
        (65, "D-较差"),
        (45, "F-危险"),
    ]
    
    print("评分 vs 健康等级:")
    for target_score, expected_grade in test_scores:
        # 构造数据使总分接近目标分数
        result = calculator.calculate(
            performance_metrics={'value': 25.0},
            anomaly_count=int((100 - target_score) * 2),
            total_count=1000,
            trend_direction="平稳",
            uptime_hours=target_score * 7.2
        )
        
        actual_score = result['total_score']
        actual_grade = result['grade']
        
        print(f"  评分 {actual_score:5.1f} -> {actual_grade}")
        
        # 验证等级划分正确
        if actual_score >= 90:
            assert 'A-' in actual_grade, f"评分{actual_score}应为A级"
        elif actual_score >= 80:
            assert 'B-' in actual_grade, f"评分{actual_score}应为B级"
        elif actual_score >= 70:
            assert 'C-' in actual_grade, f"评分{actual_score}应为C级"
        elif actual_score >= 60:
            assert 'D-' in actual_grade, f"评分{actual_score}应为D级"
        else:
            assert 'F-' in actual_grade, f"评分{actual_score}应为F级"
    
    print("\n[OK] 健康等级划分测试通过")


def test_batch_calculation():
    """测试批量计算"""
    print_section("测试7: 批量健康评分计算")
    
    calculator = HealthScoreCalculator()
    
    # 准备多个设备的数据
    devices_data = {
        'DEVICE001': {
            'anomaly_count': 5,
            'total_count': 1000,
            'trend_direction': '平稳',
            'uptime_hours': 720.0
        },
        'DEVICE002': {
            'anomaly_count': 50,
            'total_count': 1000,
            'trend_direction': '下降',
            'uptime_hours': 600.0
        },
        'DEVICE003': {
            'anomaly_count': 150,
            'total_count': 1000,
            'trend_direction': '下降',
            'uptime_hours': 400.0
        },
    }
    
    results = calculator.batch_calculate(devices_data)
    
    print(f"批量计算 {len(results)} 个设备:")
    for device_id, result in results.items():
        print(f"  {device_id}: {result['total_score']:6.2f}分 ({result['grade']})")
    
    assert len(results) == 3, "应返回3个设备的结果"
    assert all('total_score' in r for r in results.values()), "所有结果应包含总分"
    
    # 验证设备1的评分最高
    assert results['DEVICE001']['total_score'] > results['DEVICE002']['total_score'], \
        "DEVICE001评分应高于DEVICE002"
    assert results['DEVICE002']['total_score'] > results['DEVICE003']['total_score'], \
        "DEVICE002评分应高于DEVICE003"
    
    print("\n[OK] 批量计算测试通过")


def test_custom_weights():
    """测试自定义权重"""
    print_section("测试8: 自定义权重配置")
    
    # 默认权重
    calculator_default = HealthScoreCalculator()
    
    # 自定义权重（强调异常频率）
    custom_weights = {
        HealthDimension.PERFORMANCE: 0.20,
        HealthDimension.ANOMALY: 0.50,  # 提高异常权重
        HealthDimension.TREND: 0.20,
        HealthDimension.UPTIME: 0.10,
    }
    calculator_custom = HealthScoreCalculator(weights=custom_weights)
    
    # 相同数据，不同权重
    data = {
        'anomaly_count': 100,  # 较多异常
        'total_count': 1000,
        'trend_direction': '平稳',
        'uptime_hours': 720.0
    }
    
    result_default = calculator_default.calculate(**data)
    result_custom = calculator_custom.calculate(**data)
    
    print("默认权重:")
    print(f"  性能30%, 异常25%, 趋势25%, 运行20%")
    print(f"  总评分: {result_default['total_score']:.2f}")
    
    print("\n自定义权重:")
    print(f"  性能20%, 异常50%, 趋势20%, 运行10%")
    print(f"  总评分: {result_custom['total_score']:.2f}")
    
    # 由于异常较多，提高异常权重后总分应降低
    assert result_custom['total_score'] < result_default['total_score'], \
        "提高异常权重后，有异常的设备评分应降低"
    
    print("\n[OK] 自定义权重测试通过")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试9: 边界情况处理")
    
    calculator = HealthScoreCalculator()
    
    # 测试1: 无性能指标
    result1 = calculator.calculate(
        performance_metrics=None,
        anomaly_count=10,
        total_count=1000
    )
    print(f"无性能指标: {result1['total_score']:.2f}分")
    assert result1['total_score'] > 0, "无性能指标应使用默认值"
    
    # 测试2: 零数据点
    result2 = calculator.calculate(
        anomaly_count=0,
        total_count=0
    )
    print(f"零数据点: {result2['total_score']:.2f}分")
    
    # 测试3: 零运行时长
    result3 = calculator.calculate(
        uptime_hours=0
    )
    print(f"零运行时长: {result3['total_score']:.2f}分")
    assert result3['total_score'] < 100, "零运行时长应影响评分"
    
    # 测试4: 超长运行时长
    result4 = calculator.calculate(
        uptime_hours=1440.0,  # 60天，超过期望30天
        total_count=1000
    )
    print(f"超长运行时长: {result4['total_score']:.2f}分")
    
    print("\n[OK] 边界情况测试通过")


def main():
    """主测试流程"""
    print("=" * 60)
    print("  健康评分服务测试")
    print("=" * 60)
    
    try:
        test_performance_scorer()
        test_anomaly_scorer()
        test_trend_scorer()
        test_uptime_scorer()
        test_health_score_calculator()
        test_health_grades()
        test_batch_calculation()
        test_custom_weights()
        test_edge_cases()
        
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

