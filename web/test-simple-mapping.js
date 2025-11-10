// 简单的API映射测试
console.log('开始测试...')

// 直接导入映射
import { pageApiHelper } from './src/utils/api-v2-migration.js'

// 测试映射
const pathConverter = pageApiHelper.pathConverter
const mapping = pathConverter.mapping

console.log('映射对象:', mapping)
console.log('GET /apis 映射:', mapping['GET /apis'])
console.log('所有包含apis的映射:')
Object.keys(mapping)
  .filter((key) => key.includes('apis'))
  .forEach((key) => {
    console.log(`  ${key} -> ${mapping[key]}`)
  })

// 测试转换
try {
  const result = pathConverter.convertPath('GET', '/apis')
  console.log('转换结果:', result)
} catch (error) {
  console.error('转换失败:', error.message)
}
