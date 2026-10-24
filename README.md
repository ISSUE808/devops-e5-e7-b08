# B 组 DRAFT：E5–E7 集成版本

本仓库以 `DevOps_1020_Student_Cloud.zip` 的 B-draft 教学参考实现为基线，整合本组固定候选及成员 3 的新增测试。真实 GitHub CI、main 分支保护、失败 PR 拒绝及同一 PR 修复合并已完成；报告和验收表已整理，尚有交接资料待补，不能据此宣布全组实验全部验收。

报告入口：[实验报告](docs/实验报告.md)、[验收记录](docs/验收记录.csv)、[证据索引与离线备份说明](docs/证据索引.md)。

## 代码和候选来源

- 教师提供服务实现、原有 24 项测试、门禁脚本、镜像与依赖锁文件；本轮不修改生产算法。
- 成员 3（241880492）新增镜像检查失败测试，验证可解析 stdout 不能覆盖非零退出码，失败时不得运行程序。
- 成员 4（241880546）负责接收核对、整合新增测试和本组候选、调整 CI 候选输入及归档信息，完成分支保护与失败/恢复/合并验证、报告和证据整理；另按课程演示添加并恢复 1 项 version 返回码测试。当前共 26 项服务测试。
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

预期为 26 项服务测试及五个真实场景全部通过，整体门禁退出码 0。故障场景返回 1 可以符合预期；超时场景必须在候选构建成功后发生，并有容器清理证据。旧 Makefile/Compose 属于 E4 接口，本次以 `lab_cloud.py` 为入口。上述命令供新的运行使用，不是历史证据的原始命令；后者保存在各运行目录的 `command.json`。

## CI 与证据

根目录 `.github/workflows/e7-quality-gate.yml` 的检查名为 `e7-b-quality-gate`。CI 核对本组候选与 provenance 的哈希，保存候选副本及来源记录，再扫描源码/历史、构建和扫描服务镜像、运行完整门禁；无论通过或失败都归档 `work/ci/`，保留 14 天。

|阶段|真实记录|结果|
|---|---|---|
|正常 CI|[39992014649](https://github.com/ISSUE808/devops-e5-e7-b08/actions/runs/39992014649)|当时 25 项测试及五场景通过|
|PR #1 故意失败|[40077686673](https://github.com/ISSUE808/devops-e5-e7-b08/actions/runs/40077686673)|1 failed、25 passed，普通合并被实际拒绝|
|同一 PR 恢复|[40080265595](https://github.com/ISSUE808/devops-e5-e7-b08/actions/runs/40080265595)|26 项测试及五场景通过|
|合并后 main|[40080532893](https://github.com/ISSUE808/devops-e5-e7-b08/actions/runs/40080532893)|26 项测试及五场景通过|

[PR #1](https://github.com/ISSUE808/devops-e5-e7-b08/pull/1) 已正常合并为 `9fa0267fb51f9572a59dcb706d4f9bb0ffff0baf`。必需检查为 `e7-b-quality-gate`，要求分支保持最新并约束管理员；未使用绕过。演示修正的是故意写错的测试预期，不是生产算法缺陷。原始 artifact、拒绝合并日志和配置快照已下载，离线位置见证据索引。

## 已知限制与配套材料

- 本实验验证 hello E3 教学样例及保存的模型候选，不是完整在线模型迭代或论文项目全集复现。
- 已接收 E5/E6/E7 原始材料，并在本地忽略目录 `work/handoff/` 保留副本；E5 独立手工复建/运行日志仍有缺口，需补充或确认能否交叉引用 E6 成功证据。不要改写历史包。
- 云主机系统、资源与工具版本快照以及成员 1、2 的姓名学号尚未随交接材料提供，验收表保留为 PENDING；CI 环境信息不替代云主机环境信息。
- 学生包 `docs/03_B轨道操作指南.md`、`docs/04_GitHub_CI与合并门禁.md`、`ci/` 和 `templates/` 是配套指南、演示配置及报告模板；本地位于仓库外的 `course-support/`，其相对路径不等同于原学生包的 `../../ci/`。
- `work/` 默认忽略，但最终需另外备份并交付原始日志及下载的 CI artifact；禁止提交 `.env`、Token、SSH 私钥或登录文件。
