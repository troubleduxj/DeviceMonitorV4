#!/usr/bin/env node
/**
 * 批量删除功能前端测试执行脚本
 */
const { execSync } = require('child_process')
const path = require('path')

console.log('🧪 运行批量删除功能前端测试...\n')

const testFiles = [
  'tests/composables/useBatchDelete.test.js',
  'tests/composables/useBatchDelete.edge-cases.test.js',
  'tests/components/BatchDeleteComponents.test.js',
  'tests/components/BatchDeleteComponents.error-scenarios.test.js',
]

let totalTests = 0
let passedTests = 0
let failedTests = 0

for (const testFile of testFiles) {
  console.log(`📝 运行 ${testFile}...`)

  try {
    const result = execSync(`npm run test -- --run ${testFile}`, {
      cwd: __dirname,
      encoding: 'utf8',
      stdio: 'pipe',
    })

    console.log(`✅ ${testFile} 通过`)
    passedTests++

    // 解析测试结果
    const lines = result.split('\n')
    const testCountLine = lines.find((line) => line.includes('Test Files'))
    if (testCountLine) {
      const match = testCountLine.match(/(\d+) passed/)
      if (match) {
        totalTests += parseInt(match[1])
      }
    }
  } catch (error) {
    console.log(`❌ ${testFile} 失败`)
    console.log(`错误输出:\n${error.stdout || error.message}`)
    failedTests++
  }

  console.log('')
}

console.log('📊 测试结果摘要:')
console.log(`总测试文件: ${testFiles.length}`)
console.log(`通过: ${passedTests}`)
console.log(`失败: ${failedTests}`)
console.log(`成功率: ${((passedTests / testFiles.length) * 100).toFixed(1)}%`)

if (failedTests === 0) {
  console.log('🎉 所有前端测试都通过了！')
  process.exit(0)
} else {
  console.log(`⚠️ 有 ${failedTests} 个测试文件失败`)
  process.exit(1)
}
