import os
import re
from typing import List, Set, Dict

from loguru import logger

from app.base import APPBase

class V2ray(APPBase):
    def __init__(self, blockList:List[str], unblockList:List[str], filterDict:Dict[str,str], filterList:List[str], filterList_var:List[str], ChinaSet:Set[str], fileName:str, sourceRule:str):
        super(V2ray, self).__init__(blockList, unblockList, filterDict, filterList, filterList_var, ChinaSet, fileName, sourceRule)

    def __clean_category_ads_all(self):
        """
        清洗 V2Ray domain-list-community 中的 category-ads-all 文件
        移除所有非域名格式的行（IP段、纯IP、包含路径的规则等）
        """
        # 定位 domain-list-community 目录
        base_dir = os.path.dirname(self.fileName)  # 通常是 rules/
        domain_list_dir = os.path.join(base_dir, '..', 'domain-list-community')
        ads_file = os.path.join(domain_list_dir, 'adblock', 'category-ads-all')
        
        if not os.path.exists(ads_file):
            logger.warning(f"未找到 domain-list-community/adblock/category-ads-all，跳过清洗")
            return
        
        logger.info("清洗 domain-list-community/adblock/category-ads-all，过滤非域名格式...")
        
        # 读取原始内容
        with open(ads_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤规则：
        # 1. 跳过空行和注释行
        # 2. 跳过包含 / 的 CIDR 格式（如 216.239.35.0/24）
        # 3. 跳过纯 IP 格式（如 1.2.3.4）
        # 4. 跳过包含通配符 * 的行（非标准域名）
        # 5. 跳过包含 : 的行（可能是 IPv6）
        # 6. 跳过包含 . 少于1个的（不是合法域名）
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            if raw.startswith('#'):
                cleaned_lines.append(line)  # 保留注释行（但不影响编译）
                continue
            # 检查是否为有效域名格式
            # 1. 去除通配符前缀
            domain = raw
            if domain.startswith('*.') or domain.startswith('+.'):
                domain = domain[2:]
            # 2. 如果包含 / 则跳过（CIDR 或路径）
            if '/' in domain:
                logger.debug(f"跳过 CIDR/路径格式: {raw}")
                removed_count += 1
                continue
            # 3. 如果包含 * 且不是通配符域名的合法用法，跳过
            if '*' in domain and not domain.startswith('*.'):
                logger.debug(f"跳过包含非法通配符: {raw}")
                removed_count += 1
                continue
            # 4. 检查是否为纯 IP（纯数字和点组成）
            if re.match(r'^[\d\.]+$', domain):
                logger.debug(f"跳过纯 IP: {raw}")
                removed_count += 1
                continue
            # 5. 检查是否为域名（至少包含一个点，且不包含空格等特殊字符）
            if '.' not in domain or len(domain) < 4:
                logger.debug(f"跳过非域名格式: {raw}")
                removed_count += 1
                continue
            cleaned_lines.append(line)
        
        # 写回文件
        with open(ads_file, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        logger.info(f"清洗完成，移除了 {removed_count} 条非域名格式记录")

    def generate(self, isLite=False):
        try:
            if isLite:
                logger.info("generate adblock V2ray/Xray Lite...")
                fileName = self.fileNameLite
                blockList = self.blockListLite
            else:
                logger.info("generate adblock V2ray/Xray...")
                fileName = self.fileName
                blockList = self.blockList

            if os.path.exists(fileName):
                os.remove(fileName)

            # 生成规则文件
            with open(fileName, 'a', encoding='utf-8') as f:
                f.write("#\n")
                if isLite:
                    f.write("# Title: AdBlock V2ray/Xray Lite\n")
                    f.write("# Description: 适用于 V2ray、Xray 的去广告合并规则，每 8 个小时更新一次。规则源：%s。Lite 版仅针对国内域名拦截。\n"%(self.sourceRule))
                else:
                    f.write("# Title: AdBlock V2ray/Xray\n")
                    f.write("# Description: 适用于 V2ray、Xray 的去广告合并规则，每 8 个小时更新一次。规则源：%s。\n"%(self.sourceRule))
                f.write("# Homepage: %s\n"%(self.homepage))
                f.write("# Source: %s/%s\n"%(self.source, os.path.basename(fileName)))
                f.write("# Version: %s\n"%(self.version))
                f.write("# Last modified: %s\n"%(self.time))
                f.write("# Blocked domains: %s\n"%(len(blockList)))
                f.write("#\n")
                for domain in blockList:
                    if domain.find('_') < 0: # domain-list-community 工具在生成 geosite.dat 时，会进行严格的主机名校验
                        f.write("%s @ads\n"%(domain))

            # ========== 新增：清洗 domain-list-community 数据 ==========
            self.__clean_category_ads_all()
            # ========================================================

            if isLite:
                logger.info("adblock V2ray/Xray Lite: block=%d" % (len(blockList)))
            else:
                logger.info("adblock V2ray/Xray: block=%d" % (len(blockList)))
        except Exception as e:
            logger.error("%s" % (e))