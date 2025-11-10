// 测试API路径映射
import { pageApiHelper } from './src/utils/api-v2-migration.js'

console.log('测试API路径映射...')

// 测试路径转换
const pathConverter = pageApiHelper.pathConverter

try {
  // 测试APIs路径映射
  const apisPath = pathConverter.convertPath('GET', '/apis')
  console.log('GET /apis 映射结果:', apisPath)

  // 测试其他路径
  const userPath = pathConverter.convertPath('GET', '/users')
  console.log('GET /users 映射结果:', userPath)

  // 测试系统API创建
  const systemApis = pageApiHelper.createSystemApis()
  console.log('系统APIs对象:', Object.keys(systemApis))

  // 测试apis对象
  if (systemApis.apis) {
    console.log('APIs对象方法:', Object.keys(systemApis.apis))
  } else {
    console.error('APIs对象不存在!')
  }
} catch (error) {
  console.error('测试失败:', error)
}
