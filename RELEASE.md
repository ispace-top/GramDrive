# 版本发布流程

## 使用 GitHub Actions 自动发布

### 发布步骤

1. **进入 Actions 页面**
   - 访问仓库的 Actions 标签页
   - 选择左侧的 "发布新版本" 工作流

2. **手动触发发布**
   - 点击右上角的 "Run workflow" 按钮
   - 填写版本号（例如：`1.0.1`）
   - 填写版本更新说明（可选）
   - 点击 "Run workflow" 确认

3. **自动执行流程**
   - ✅ 自动更新 `app/version.py` 中的版本号
   - ✅ 提交版本更新到 main 分支
   - ✅ 创建对应的 Git Tag（例如：`v1.0.1`）
   - ✅ 生成更新日志（基于 Git 提交记录）
   - ✅ 创建 GitHub Release
   - ✅ 自动触发 Docker 镜像构建

4. **验证发布**
   - 检查 [Releases](https://github.com/ispace-top/GramDrive/releases) 页面
   - 确认新版本已发布
   - 检查 Docker Hub 是否已推送新镜像

## 手动发布（备用方案）

如果 GitHub Actions 不可用，可以手动执行以下步骤：

### 1. 更新版本号

编辑 `app/version.py` 文件：

```python
__version__ = "1.0.1"  # 修改为新版本号
```

### 2. 提交更改

```bash
git add app/version.py
git commit -m "chore: 发布版本 1.0.1"
git push origin main
```

### 3. 创建 Tag

```bash
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

### 4. 创建 GitHub Release

- 访问仓库的 Releases 页面
- 点击 "Draft a new release"
- 选择刚创建的 Tag：`v1.0.1`
- 填写 Release 标题和描述
- 点击 "Publish release"

### 5. 构建 Docker 镜像

```bash
# 本地构建（可选）
docker build -t ispacetop/gramdrive:1.0.1 .
docker push ispacetop/gramdrive:1.0.1

# 或等待 GitHub Actions 自动构建
```

## 版本号规范

建议遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号（Major）**：不兼容的 API 修改
  - 例如：`1.0.0` → `2.0.0`

- **次版本号（Minor）**：向下兼容的功能性新增
  - 例如：`1.0.0` → `1.1.0`

- **修订号（Patch）**：向下兼容的问题修正
  - 例如：`1.0.0` → `1.0.1`

## 提交信息规范

为了生成更好的更新日志，建议使用以下提交信息格式：

- `feat:` - 新功能
  - 例如：`feat: 添加文件标签功能`

- `fix:` - 问题修复
  - 例如：`fix: 修复下载进度显示错误`

- `docs:` - 文档更新
  - 例如：`docs: 更新使用指南`

- `style:` - 代码格式调整
  - 例如：`style: 优化代码格式`

- `refactor:` - 代码重构
  - 例如：`refactor: 重构下载服务模块`

- `perf:` - 性能优化
  - 例如：`perf: 优化缩略图生成速度`

- `test:` - 测试相关
  - 例如：`test: 添加单元测试`

- `chore:` - 构建/工具相关
  - 例如：`chore: 更新依赖版本`

## 发布检查清单

发布前请确认：

- [ ] 所有测试通过
- [ ] 更新了 CHANGELOG.md（可选）
- [ ] 更新了文档（如有 API 变更）
- [ ] 代码已合并到 main 分支
- [ ] 版本号符合语义化版本规范
- [ ] Docker 镜像构建成功
- [ ] Release Notes 描述清晰

## 常见问题

### Q: 发布失败怎么办？

**A:** 检查以下几点：
1. GitHub Actions 是否有足够的权限
2. DOCKER_USERNAME 和 DOCKER_PASSWORD secrets 是否正确配置
3. 版本号是否重复（Tag 已存在）
4. 查看 Actions 日志了解具体错误

### Q: 如何回滚版本？

**A:**
1. 不建议删除已发布的 Tag 和 Release
2. 如需修复，应该发布新的 Patch 版本
3. 紧急情况可以在 Release 页面标记为 "Pre-release"

### Q: 如何发布测试版本？

**A:**
1. 使用带后缀的版本号，如：`1.0.1-beta.1`
2. 在 GitHub Release 中勾选 "This is a pre-release"
3. Docker 镜像会自动打上对应的 tag

## 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [约定式提交规范](https://www.conventionalcommits.org/zh-hans/)
