# -*- coding: utf-8 -*-
"""
特征提取服务测试脚本
"""

import os
import sys
import numpy as np

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai.feature_extraction import (
    StatisticalFeatureExtractor,
    TimeSeriesFeatureExtractor,
    FrequencyFeatureExtractor,
    FeatureExtractor
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_statistical_features():
    """测试统计特征提取"""
    print_section("测试1: 统计特征提取")
    
    # 生成测试数据
    np.random.seed(42)
    data = np.random.normal(loc=100, scale=10, size=100).tolist()
    
    extractor = StatisticalFeatureExtractor()
    features = extractor.extract(data)
    
    print(f"数据点数: {len(data)}")
    print(f"提取特征数: {len(features)}")
    print("\n关键特征:")
    for key in ['mean', 'std', 'max', 'min', 'median']:
        if key in features:
            print(f"  {key}: {features[key]:.2f}")
    
    assert len(features) > 0, "特征提取失败"
    assert 'mean' in features, "缺少均值特征"
    assert 90 < features['mean'] < 110, "均值不在预期范围"
    
    print("\n[OK] 统计特征提取测试通过")


def test_timeseries_features():
    """测试时间序列特征提取"""
    print_section("测试2: 时间序列特征提取")
    
    # 生成上升趋势数据（增加更多点，减少噪声）
    x = np.arange(100)
    data_upward = (x * 2 + np.random.normal(0, 5, 100)).tolist()
    
    # 生成下降趋势数据
    data_downward = (200 - x * 2 + np.random.normal(0, 5, 100)).tolist()
    
    # 生成平稳数据（极小噪声）
    data_stable = np.random.normal(25, 0.5, 100).tolist()
    
    extractor = TimeSeriesFeatureExtractor()
    
    # 测试趋势检测
    trend_up = extractor.extract_trend(data_upward)
    trend_down = extractor.extract_trend(data_downward)
    trend_stable = extractor.extract_trend(data_stable)
    
    print(f"上升趋势检测: {trend_up}")
    print(f"下降趋势检测: {trend_down}")
    print(f"平稳趋势检测: {trend_stable}")
    
    assert trend_up == "上升", f"趋势检测错误: 期望上升，实际{trend_up}"
    assert trend_down == "下降", f"趋势检测错误: 期望下降，实际{trend_down}"
    assert trend_stable == "平稳", f"趋势检测错误: 期望平稳，实际{trend_stable}"
    
    # 测试变化率
    change_features = extractor.extract_change_rate(data_upward)
    print(f"\n变化率特征数: {len(change_features)}")
    print(f"平均变化: {change_features.get('avg_change', 0):.2f}")
    print(f"波动性: {change_features.get('volatility', 0):.2f}")
    
    # 测试自相关
    autocorr_features = extractor.extract_autocorrelation(data_upward, max_lag=3)
    print(f"\n自相关特征数: {len(autocorr_features)}")
    
    # 测试综合提取
    all_features = extractor.extract(data_upward)
    print(f"\n时序综合特征数: {len(all_features)}")
    
    assert len(all_features) > 0, "时序特征提取失败"
    
    print("\n[OK] 时间序列特征提取测试通过")


def test_frequency_features():
    """测试频域特征提取"""
    print_section("测试3: 频域特征提取")
    
    # 生成包含明显周期性的数据
    t = np.linspace(0, 10, 200)
    # 5Hz正弦波 + 噪声
    data = (np.sin(2 * np.pi * 5 * t) + np.random.normal(0, 0.1, 200)).tolist()
    
    extractor = FrequencyFeatureExtractor()
    features = extractor.extract(data, sampling_rate=20.0)
    
    print(f"数据点数: {len(data)}")
    print(f"采样率: 20 Hz")
    print(f"提取特征数: {len(features)}")
    
    if 'dominant_frequency' in features:
        print(f"\n主频率: {features['dominant_frequency']:.2f} Hz")
        print(f"主频幅值: {features['dominant_magnitude']:.2f}")
    
    if 'total_energy' in features:
        print(f"总能量: {features['total_energy']:.2f}")
    
    if all(key in features for key in ['low_freq_ratio', 'mid_freq_ratio', 'high_freq_ratio']):
        print(f"\n频率能量分布:")
        print(f"  低频: {features['low_freq_ratio']*100:.1f}%")
        print(f"  中频: {features['mid_freq_ratio']*100:.1f}%")
        print(f"  高频: {features['high_freq_ratio']*100:.1f}%")
    
    assert len(features) > 0, "频域特征提取失败"
    
    print("\n[OK] 频域特征提取测试通过")


def test_feature_extractor_all():
    """测试特征提取器综合功能"""
    print_section("测试4: 特征提取器综合功能")
    
    # 生成测试数据
    np.random.seed(42)
    data = np.random.normal(100, 10, 100).tolist()
    
    extractor = FeatureExtractor()
    
    # 测试单一数据特征提取
    features = extractor.extract_all_features(
        data,
        include_statistical=True,
        include_timeseries=True,
        include_frequency=True,
        sampling_rate=1.0
    )
    
    print(f"数据点数: {len(data)}")
    print(f"提取总特征数: {len(features)}")
    
    # 统计各类特征数量
    stat_count = sum(1 for k in features if k.startswith('stat_'))
    ts_count = sum(1 for k in features if k.startswith('ts_'))
    freq_count = sum(1 for k in features if k.startswith('freq_'))
    
    print(f"\n特征分类:")
    print(f"  统计特征: {stat_count}个")
    print(f"  时序特征: {ts_count}个")
    print(f"  频域特征: {freq_count}个")
    
    assert len(features) > 0, "综合特征提取失败"
    assert stat_count > 0, "统计特征缺失"
    assert ts_count > 0, "时序特征缺失"
    assert freq_count > 0, "频域特征缺失"
    
    # 测试批量提取
    data_dict = {
        'temperature': np.random.normal(25, 2, 100).tolist(),
        'pressure': np.random.normal(1013, 5, 100).tolist(),
        'humidity': np.random.normal(60, 10, 100).tolist(),
    }
    
    batch_results = extractor.extract_features_batch(
        data_dict,
        include_statistical=True,
        include_timeseries=True,
        include_frequency=False  # 关闭频域以加速
    )
    
    print(f"\n批量提取结果:")
    for metric, feat in batch_results.items():
        print(f"  {metric}: {len(feat)}个特征")
    
    assert len(batch_results) == 3, "批量提取失败"
    assert all(len(feat) > 0 for feat in batch_results.values()), "部分指标特征缺失"
    
    print("\n[OK] 综合功能测试通过")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试5: 边界情况处理")
    
    extractor = FeatureExtractor()
    
    # 空数据
    features_empty = extractor.extract_all_features([])
    print(f"空数据测试: {len(features_empty)}个特征 (期望0)")
    assert len(features_empty) == 0, "空数据应返回空特征"
    
    # 单个数据点
    features_single = extractor.extract_all_features([100.0])
    print(f"单点数据测试: {len(features_single)}个特征")
    # 单点数据可能有部分特征（如均值）
    
    # 包含NaN的数据
    data_with_nan = [1.0, 2.0, float('nan'), 4.0, 5.0]
    features_nan = extractor.extract_all_features(data_with_nan, include_frequency=False)
    print(f"含NaN数据测试: {len(features_nan)}个特征")
    assert len(features_nan) > 0, "应能处理含NaN的数据"
    
    # 全部相同的数据
    data_constant = [100.0] * 50
    features_constant = extractor.extract_all_features(data_constant, include_frequency=False)
    print(f"常数数据测试: {len(features_constant)}个特征")
    assert features_constant.get('stat_std', -1) == 0, "常数数据标准差应为0"
    
    print("\n[OK] 边界情况测试通过")


def main():
    """主测试流程"""
    print("=" * 60)
    print("  特征提取服务测试")
    print("=" * 60)
    
    try:
        test_statistical_features()
        test_timeseries_features()
        test_frequency_features()
        test_feature_extractor_all()
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

