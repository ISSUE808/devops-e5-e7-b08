# B 组 DRAFT：E5–E7 集成版本

本仓库以 `DevOps_1020_Student_Cloud.zip` 的 B-draft 教学参考实现为基线，整合本组固定候选及成员 3 的新增测试。当前完成本地整合，真实 GitHub CI、分支保护、失败 PR 拒绝与修复合并仍待执行；本地单测通过不能替代这些记录。

## 代码和候选来源

- 教师提供服务实现、原有 24 项测试、门禁脚本、镜像与依赖锁文件；本轮不修改生产算法。
- 成员 3（241880492）新增镜像检查失败测试，验证可解析 stdout 不能覆盖非零退出码，失败时不得运行程序。整合后服务测试共 25 项。
- 成员 4（241880546）负责接收核对、整合新增测试和本组候选、调整 CI 候选输入及归档信息。
- 最终候选：[group-E5-20261022.Dockerfile](fixtures/ci-candidates/group-E5-20261022.Dockerfile)；[来源记录](fixtures/ci-candidates/group-E5-20261022.provenance.json)保留原始字段，精确模型版本未单独记录。
- 原服务器位置为 `/root/devops-course/DevOps_1020_Student_Cloud/labs/B-draft/work/candidate/Dockerfile`，接收自成员 3 的 `E7-member3-241880492-20261023.tar.gz`，转存为上述仓库路径，未改变候选内容。

固定候选 SHA-256（保留 LF 换行，不要改写候选字节）：

```text
f4c86d4ee120d8a9114b1454d3eb23b5014eb326cc5b524cb291bc3f67e4eccd
```

来源记录中的 `BUILT_AND_VERIFIED` 和镜像 ID 指历史 E6 运行，不代表新提交已通过 CI。教师 DeepSeek 候选保留供显式 `--replay` 使用，但默认 CI 已改用本组候选。

## 云主机运行

在有可用 Docker 的本组 Linux 云服务器、此仓库根目录执行。使用自己的目录和镜像标签，每次重跑换新的 `--out`，不要覆盖队友证据：

```bash
python3 scripts/lab_cloud.py doctor
python3 scripts/lab_cloud.py build --image course1020-draft:241880546-e7 --out work/member4-build-01 --build-timeout 1200
python3 scripts/lab_cloud.py gate --image course1020-draft:241880546-e7 --candidate fixtures/ci-candidates/group-E5-20261022.Dockerfile --out work/member4-e7-01 --build-timeout 600
```

预期为 25 项服务测试及五个真实场景全部通过，整体门禁退出码 0。故障场景返回 1 可以符合预期；超时场景必须在候选构建成功后发生，并有容器清理证据。旧 Makefile/Compose 属于 E4 接口，本次以 `lab_cloud.py` 为入口。

## CI 与证据

根目录 `.github/workflows/e7-quality-gate.yml` 的检查名为 `e7-b-quality-gate`。CI 核对本组候选与 provenance 的哈希，保存候选副本及来源记录，再扫描源码/历史、构建和扫描服务镜像、运行完整门禁；无论通过或失败都归档 `work/ci/`，保留 14 天。

后续需保存正常、故意失败、同一 PR 修复恢复的运行链接与 artifact，配置必需检查和分支保护，实际验证普通合并被拒绝，再于最新检查通过后合并。此步骤尚未完成，不要使用教师示例链接或成员 3 的旧镜像替代新提交的 CI 证据。

## 已知限制与配套材料

- 本实验验证 hello E3 教学样例及保存的模型候选，不是完整在线模型迭代或论文项目全集复现。
- 已接收 E5/E6/E7 原始材料并保存在仓库外；E5 独立手工复建/运行日志仍有缺口，需补充或确认能否交叉引用 E6 成功证据。不要改写历史包。
- 学生包 `docs/03_B轨道操作指南.md`、`docs/04_GitHub_CI与合并门禁.md`、`ci/` 和 `templates/` 是配套指南、演示配置及报告模板；本地位于仓库外的 `course-support/`，其相对路径不等同于原学生包的 `../../ci/`。
- `work/` 默认忽略，但最终需另外备份并交付原始日志及下载的 CI artifact；禁止提交 `.env`、Token、SSH 私钥或登录文件。
