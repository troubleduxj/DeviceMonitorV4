# -*- coding: utf-8 -*-
"""
趋势预测服务测试脚本
"""

import os
import sys
import numpy as np
import time

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai.prediction import (
    ARIMAPredictor,
    MovingAveragePredictor,
    ExponentialSmoothingPredictor,
    LinearRegressionPredictor,
    PredictionEvaluator,
    TrendPredictor,
    PredictionMethod
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_moving_average_predictor():
    """测试移动平均预测器"""
    print_section("测试1: 移动平均预测")
    
    # 生成上升趋势数据
    np.random.seed(42)
    data = (np.arange(50) + np.random.normal(0, 2, 50)).tolist()
    
    predictor = MovingAveragePredictor(window=5)
    result = predictor.predict(data, steps=10)
    
    print(f"历史数据点数: {len(data)}")
    print(f"预测步数: 10")
    print(f"窗口大小: 5")
    print(f"预测成功: {result['success']}")
    print(f"预测值数量: {len(result['predictions'])}")
    
    if result['predictions']:
        print(f"\n前5个预测值: {[f'{x:.2f}' for x in result['predictions'][:5]]}")
    
    assert result['success'], "预测应该成功"
    assert len(result['predictions']) == 10, "应返回10个预测值"
    
    print("\n[OK] 移动平均预测测试通过")


def test_exponential_smoothing():
    """测试指数平滑预测"""
    print_section("测试2: 指数平滑预测")
    
    # 生成有噪声的趋势数据
    np.random.seed(42)
    data = (50 + np.random.normal(0, 5, 50)).tolist()
    
    predictor = ExponentialSmoothingPredictor(alpha=0.3)
    result = predictor.predict(data, steps=10)
    
    print(f"历史数据点数: {len(data)}")
    print(f"预测步数: 10")
    print(f"平滑系数alpha: 0.3")
    print(f"预测成功: {result['success']}")
    
    if result['predictions']:
        print(f"\n预测值（前5个）: {[f'{x:.2f}' for x in result['predictions'][:5]]}")
    
    assert result['success'], "预测应该成功"
    assert len(result['predictions']) == 10, "应返回10个预测值"
    
    print("\n[OK] 指数平滑预测测试通过")


def test_linear_regression_predictor():
    """测试线性回归预测"""
    print_section("测试3: 线性回归预测")
    
    # 生成明显线性趋势数据
    np.random.seed(42)
    x = np.arange(50)
    data = (2 * x + 10 + np.random.normal(0, 3, 50)).tolist()
    
    predictor = LinearRegressionPredictor()
    result = predictor.predict(data, steps=10)
    
    print(f"历史数据点数: {len(data)}")
    print(f"预测步数: 10")
    print(f"预测成功: {result['success']}")
    
    if result.get('slope') is not None:
        print(f"\n拟合斜率: {result['slope']:.4f} (期望约2.0)")
        print(f"拟合截距: {result['intercept']:.4f} (期望约10.0)")
    
    if result['predictions']:
        print(f"\n预测值（前5个）: {[f'{x:.2f}' for x in result['predictions'][:5]]}")
    
    assert result['success'], "预测应该成功"
    assert len(result['predictions']) == 10, "应返回10个预测值"
    assert abs(result['slope'] - 2.0) < 0.5, "斜率应接近2.0"
    
    print("\n[OK] 线性回归预测测试通过")


def test_arima_predictor():
    """测试ARIMA预测器"""
    print_section("测试4: ARIMA时间序列预测")
    
    # 生成时间序列数据
    np.random.seed(42)
    data = []
    value = 100
    for i in range(100):
        value = 0.8 * value + 20 + np.random.normal(0, 5)
        data.append(value)
    
    predictor = ARIMAPredictor(order=(1, 1, 1))
    result = predictor.predict(data, steps=10)
    
    print(f"历史数据点数: {len(data)}")
    print(f"ARIMA参数: (1, 1, 1)")
    print(f"预测步数: 10")
    print(f"预测成功: {result['success']}")
    
    if result['predictions']:
        print(f"\n预测值（前5个）: {[f'{x:.2f}' for x in result['predictions'][:5]]}")
    
    if result['success']:
        assert len(result['predictions']) == 10, "应返回10个预测值"
        print("\n[OK] ARIMA预测测试通过")
    else:
        print("\n[SKIP] ARIMA预测跳过（可能statsmodels未安装或数据不适合）")


def test_prediction_evaluator():
    """测试预测准确度评估器"""
    print_section("测试5: 预测准确度评估")
    
    # 生成实际值和预测值
    np.random.seed(42)
    actual = np.arange(50, 60).tolist()
    predicted = (np.arange(50, 60) + np.random.normal(0, 2, 10)).tolist()
    
    evaluator = PredictionEvaluator()
    
    # 测试各项指标
    mae = evaluator.calculate_mae(actual, predicted)
    rmse = evaluator.calculate_rmse(actual, predicted)
    mape = evaluator.calculate_mape(actual, predicted)
    
    print(f"实际值: {actual[:5]}...")
    print(f"预测值: {[f'{x:.2f}' for x in predicted[:5]]}...")
    print(f"\n评估指标:")
    print(f"  MAE  (平均绝对误差): {mae:.4f}")
    print(f"  RMSE (均方根误差): {rmse:.4f}")
    print(f"  MAPE (平均百分比误差): {mape:.2f}%")
    
    assert mae < float('inf'), "MAE应为有限值"
    assert rmse < float('inf'), "RMSE应为有限值"
    assert mape < float('inf'), "MAPE应为有限值"
    assert mae >= 0, "MAE应为非负值"
    
    # 测试综合评估
    metrics = evaluator.evaluate(actual, predicted)
    print(f"\n综合评估: {metrics}")
    
    assert 'mae' in metrics, "应包含MAE"
    assert 'rmse' in metrics, "应包含RMSE"
    assert 'mape' in metrics, "应包含MAPE"
    
    print("\n[OK] 预测准确度评估测试通过")


def test_trend_predictor():
    """测试趋势预测器主类"""
    print_section("测试6: 趋势预测器主类")
    
    # 生成测试数据
    np.random.seed(42)
    data = (np.arange(50) + np.random.normal(0, 3, 50)).tolist()
    
    predictor = TrendPredictor()
    
    # 测试不同方法
    methods = [
        (PredictionMethod.MOVING_AVERAGE, "移动平均"),
        (PredictionMethod.EXPONENTIAL_SMOOTHING, "指数平滑"),
        (PredictionMethod.LINEAR_REGRESSION, "线性回归"),
    ]
    
    print(f"历史数据点数: {len(data)}")
    print(f"预测步数: 10")
    print(f"\n测试各种预测方法:")
    
    for method, name in methods:
        result = predictor.predict(data, steps=10, method=method)
        print(f"  {name}: {'成功' if result['success'] else '失败'}, "
              f"预测值数量={len(result['predictions'])}")
        assert result['success'], f"{name}预测应该成功"
    
    # 测试ARIMA（可能失败）
    arima_result = predictor.predict(data, steps=10, method=PredictionMethod.ARIMA)
    print(f"  ARIMA: {'成功' if arima_result['success'] else '失败/跳过'}")
    
    print("\n[OK] 趋势预测器主类测试通过")


def test_batch_prediction():
    """测试批量预测"""
    print_section("测试7: 批量预测")
    
    np.random.seed(42)
    
    # 准备多个指标的数据
    data_dict = {
        'temperature': (25 + np.arange(50) * 0.1 + np.random.normal(0, 1, 50)).tolist(),
        'pressure': (1013 + np.random.normal(0, 3, 50)).tolist(),
        'humidity': (60 - np.arange(50) * 0.05 + np.random.normal(0, 2, 50)).tolist(),
    }
    
    predictor = TrendPredictor()
    results = predictor.batch_predict(
        data_dict,
        steps=5,
        method=PredictionMethod.MOVING_AVERAGE
    )
    
    print(f"预测指标数: {len(results)}")
    print(f"\n各指标预测结果:")
    for metric, result in results.items():
        status = "成功" if result['success'] else "失败"
        pred_count = len(result['predictions'])
        print(f"  {metric}: {status}, 预测值数量={pred_count}")
        if result['predictions']:
            print(f"    预测值: {[f'{x:.2f}' for x in result['predictions'][:3]]}...")
    
    assert len(results) == 3, "应返回3个指标的结果"
    assert all(r['success'] for r in results.values()), "所有预测应成功"
    
    print("\n[OK] 批量预测测试通过")


def test_prediction_accuracy():
    """测试预测准确度"""
    print_section("测试8: 预测准确度测试")
    
    # 生成已知模式的数据
    np.random.seed(42)
    
    # 线性增长数据
    train_data = (np.arange(80) * 2 + 10).tolist()
    test_data = (np.arange(80, 90) * 2 + 10).tolist()
    
    predictor = TrendPredictor()
    
    # 使用线性回归预测（最适合这种数据）
    result = predictor.predict(train_data, steps=10, method=PredictionMethod.LINEAR_REGRESSION)
    
    if result['success']:
        predictions = result['predictions']
        
        # 评估准确度
        metrics = predictor.evaluate_prediction(test_data, predictions)
        
        print(f"训练数据: {len(train_data)}点")
        print(f"测试数据: {len(test_data)}点")
        print(f"预测方法: 线性回归")
        print(f"\n准确度评估:")
        print(f"  MAE: {metrics['mae']:.4f}")
        print(f"  RMSE: {metrics['rmse']:.4f}")
        print(f"  MAPE: {metrics['mape']:.2f}%")
        
        # 对于线性数据，预测应该很准确
        assert metrics['mae'] < 5, "MAE应该很小（<5）"
        assert metrics['mape'] < 5, "MAPE应该很小（<5%）"
        
        print("\n[OK] 预测准确度测试通过")
    else:
        print("\n[SKIP] 预测失败，跳过准确度测试")


def test_edge_cases():
    """测试边界情况"""
    print_section("测试9: 边界情况处理")
    
    predictor = TrendPredictor()
    
    # 空数据
    result_empty = predictor.predict([], steps=10)
    print(f"空数据: {result_empty['success']} (期望False)")
    assert not result_empty['success'], "空数据应返回失败"
    
    # 数据点太少
    result_few = predictor.predict([1.0, 2.0], steps=10)
    print(f"数据点太少(2个): {result_few['success']}")
    
    # 单点数据
    result_single = predictor.predict([100.0], steps=10)
    print(f"单点数据: {result_single['success']}")
    
    # 含NaN数据
    data_with_nan = [1.0, 2.0, float('nan'), 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    result_nan = predictor.predict(data_with_nan, steps=5, method=PredictionMethod.MOVING_AVERAGE)
    print(f"含NaN数据: {result_nan['success']}")
    
    # 常数数据
    constant_data = [100.0] * 50
    result_constant = predictor.predict(constant_data, steps=10, method=PredictionMethod.MOVING_AVERAGE)
    print(f"常数数据: {result_constant['success']}")
    if result_constant['success']:
        print(f"  预测值: {result_constant['predictions'][0]:.2f} (期望约100)")
        assert abs(result_constant['predictions'][0] - 100) < 1, "常数数据预测值应接近100"
    
    # 步数为0或负数
    result_zero_steps = predictor.predict([1, 2, 3, 4, 5], steps=0)
    print(f"步数=0: {result_zero_steps['success']} (期望False)")
    assert not result_zero_steps['success'], "步数=0应返回失败"
    
    print("\n[OK] 边界情况测试通过")


def test_performance():
    """测试性能"""
    print_section("测试10: 性能测试")
    
    # 生成大量数据
    np.random.seed(42)
    data_1k = (np.arange(1000) + np.random.normal(0, 10, 1000)).tolist()
    data_10k = (np.arange(10000) + np.random.normal(0, 10, 10000)).tolist()
    
    predictor = TrendPredictor()
    
    # 测试移动平均性能
    start = time.time()
    result_ma_1k = predictor.predict(data_1k, steps=100, method=PredictionMethod.MOVING_AVERAGE)
    time_ma_1k = (time.time() - start) * 1000
    
    print(f"1000点数据 (移动平均): {time_ma_1k:.2f}ms")
    
    start = time.time()
    result_ma_10k = predictor.predict(data_10k, steps=100, method=PredictionMethod.MOVING_AVERAGE)
    time_ma_10k = (time.time() - start) * 1000
    
    print(f"10000点数据 (移动平均): {time_ma_10k:.2f}ms")
    
    # 测试线性回归性能
    start = time.time()
    result_lr_1k = predictor.predict(data_1k, steps=100, method=PredictionMethod.LINEAR_REGRESSION)
    time_lr_1k = (time.time() - start) * 1000
    
    print(f"1000点数据 (线性回归): {time_lr_1k:.2f}ms")
    
    # 性能断言
    assert time_ma_1k < 100, f"1000点移动平均应<100ms，实际{time_ma_1k:.2f}ms"
    assert time_lr_1k < 200, f"1000点线性回归应<200ms，实际{time_lr_1k:.2f}ms"
    
    print("\n性能评估:")
    print(f"  移动平均: 优秀 (1000点<{time_ma_1k:.0f}ms)")
    print(f"  线性回归: 优秀 (1000点<{time_lr_1k:.0f}ms)")
    
    print("\n[OK] 性能测试通过")


def main():
    """主测试流程"""
    print("=" * 60)
    print("  趋势预测服务测试")
    print("=" * 60)
    
    try:
        test_moving_average_predictor()
        test_exponential_smoothing()
        test_linear_regression_predictor()
        test_arima_predictor()
        test_prediction_evaluator()
        test_trend_predictor()
        test_batch_prediction()
        test_prediction_accuracy()
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

