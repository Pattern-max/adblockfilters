import os
from loguru import logger
from readme import ReadMe
from updater import Updater
from filter import Filter

# 设置日志级别为 INFO
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

pwd = os.getcwd()
readme = ReadMe(pwd + '/README.md')
ruleList = readme.getRules()
logger.info(f"从 README 读取到 {len(ruleList)} 条规则")

if not ruleList:
    logger.error("没有读取到任何规则，请检查 README.md 格式！")
    exit(1)

# 更新上游规则（下载）
updater = Updater(ruleList)
update, ruleList = updater.update(pwd + '/rules')
logger.info(f"更新后规则数量: {len(ruleList)}")

if not ruleList:
    logger.error("更新后规则列表为空，无法生成！")
    exit(1)

# 生成最终规则
logger.info("开始生成最终规则文件...")
filter_obj = Filter(ruleList, pwd + '/rules')
filter_obj.generate(readme.getRulesNames())
logger.info("生成完成！请检查 rules/ 目录。")