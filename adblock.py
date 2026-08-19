import os

from loguru import logger
from tld.utils import update_tld_names

from readme import ReadMe
from updater import Updater
from filter import Filter

class ADBlock(object):
    def __init__(self):
        self.pwd = os.getcwd()

    def refresh(self):
        readme = ReadMe(self.pwd + '/README.md')
        ruleList = readme.getRules()
        
        # 调试：打印从 README 读取到的规则数量
        logger.info(f"从 README 读取到 {len(ruleList)} 条规则")
        for rule in ruleList:
            logger.info(f"  - {rule.name} ({rule.type})")
        
        '''
        # for test
        testList = []
        for rule in ruleList:
            if rule.type in ['filter']:
                testList.append(rule)
        ruleList = testList
        '''
        
        # 更新上游规则
        updater = Updater(ruleList)
        update, ruleList = updater.update(self.pwd + '/rules')
        
        # 调试：打印更新后的规则数量
        logger.info(f"更新后 ruleList 数量: {len(ruleList)}")
        
        # 强制生成规则，无论上游是否有更新
        # if not update:
        #     return
        update = True
        
        # 调试：确认 ruleList 不为空
        if not ruleList:
            logger.error("ruleList 为空！无法生成规则！")
            return
        
        # 生成新规则
        logger.info("开始生成最终规则文件...")
        filter = Filter(ruleList, self.pwd + '/rules')
        filter.generate(readme.getRulesNames())
        logger.info("规则文件生成完成！")
        
        # 生成 readme.md
        readme.setRules(ruleList)
        readme.regenerate()
        

if __name__ == '__main__':
    '''
    # for test
    logFile = os.getcwd() + "/adblock.log"
    if os.path.exists(logFile):
        os.remove(logFile)
    logger.add(logFile)
    '''
    # 更新 tld
    update_tld_names()
    
    adBlock = ADBlock()
    adBlock.refresh()