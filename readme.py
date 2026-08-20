import re
import os
from typing import List

from loguru import logger

class Rule(object):
    def __init__(self, name:str, type:str, url:str, latest:str, update:bool=False):
        self.name = name
        self.filename = self.name.replace(' ', '_') + '.txt'
        self.type = type
        self.url = url
        self.latest = latest
        self.update = update

# redme文件操作
class ReadMe(object):
    def __init__(self, filename:str):
        self.filename = filename
        self.ruleList:List[Rule] = []
        self.proxyList = [
            "",
            "https://gcore.jsdelivr.net/gh",
            "https://github.boki.moe",
            "https://ghfast.top"
        ]

    def getRules(self) -> List[Rule]:
        logger.info("resolve readme...")
        self.ruleList = []
        with open(self.filename, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        # 寻找 "上游规则源" 表格
        in_upstream_table = False
        for line in lines:
            line = line.replace('\r', '').replace('\n', '').strip()
            if not line:
                continue
            
            # 检测表格开始：必须是 "| 规则 | 类型 | 原始链接 |" 开头
            if line == '| 规则 | 类型 | 原始链接 |' or line.startswith('| 规则 | 类型 | 原始链接 |'):
                in_upstream_table = True
                continue
            
            # 如果在表格中，检测结束条件
            if in_upstream_table:
                # 遇到空行或下一个标题（### 或 ##）则停止
                if line.startswith('###') or line.startswith('##') or line == '' or line.startswith('---'):
                    break
                # 解析表格行（必须是以 | 开头且不是分隔行）
                if line.startswith('|') and not line.startswith('|:-'):
                    parts = list(map(lambda x: x.strip(), line[1:-1].split('|')))
                    # 至少需要 3 列：名称、类型、原始链接
                    if len(parts) >= 3 and parts[0] and parts[0] != '规则' and not parts[0].startswith('-'):
                        name = parts[0]
                        rule_type = parts[1] if len(parts) > 1 else 'dns'
                        # 提取原始链接
                        url_part = parts[2] if len(parts) > 2 else ''
                        url = ''
                        if '(' in url_part and ')' in url_part:
                            url = url_part[url_part.find('(')+1:url_part.find(')')]
                        # 获取更新日期（最后一列）
                        latest = parts[-1] if len(parts) > 3 else ''
                        if url and name and name != '规则':
                            self.ruleList.append(Rule(name, rule_type, url, latest))
        
        logger.info(f"从上游规则源表格解析到 {len(self.ruleList)} 条规则")
        return self.ruleList

    def getRulesNames(self) -> str:
        names = ""
        for rule in self.ruleList:
            names += rule.name + '、'
        return names[:-1]

    def setRules(self, ruleList:List[Rule]):
        self.ruleList = ruleList

    def __subscribeLink(self, fileName:str, url:str=None):
        link = ""
        if url:
            link += " [原始链接](%s) |" % (url)
        else:
            link += " [原始链接](https://raw.githubusercontent.com/Pattern-max/adblockfilters/main/rules/%s) |" % (fileName)
        for i in range(1, len(self.proxyList)):
            proxy = self.proxyList[i]
            if proxy.startswith("https://gcore.jsdelivr.net/"):
                link += " [加速链接%d](%s/Pattern-max/adblockfilters@main/rules/%s) |" % (i, proxy, fileName)
            else:
                link += " [加速链接%d](%s/https://raw.githubusercontent.com/Pattern-max/adblockfilters/main/rules/%s) |" % (i, proxy, fileName)
        return link
    
    def regenerate(self):
        logger.info("regenerate readme...")
        if os.path.exists(self.filename):
            os.remove(self.filename)
        
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write("# AdBlock DNS Filters\n")
            f.write("去广告合并规则，每8个小时更新一次。  \n")
            f.write("个人收藏了不少广告过滤规则，但是每次往新设备添加的时候很是头疼，于是写了这个项目，定时自动获取各规则源更新，生成合并规则库。\n")
            f.write("\n")

            f.write("## 说明\n")
            f.write("1. 定时从上游各规则源获取更新，合并去重。\n")
            f.write("2. 使用国内、国外各 3 组 DNS 服务，分别对上游各规则源拦截的域名进行解析，去除已无法解析的域名。（上游各规则源中存在大量已无法解析的域名，无需加入拦截规则）\n")
            f.write("3. 本项目仅对上游规则进行合并、去重、去除无效域名，不做任何修改。如发现误拦截情况，可临时添加放行规则（如 `@@||www.example.com^$important`），并向上游规则反馈。\n")
            f.write("\n")

            f.write("## 订阅链接\n")
            f.write("1. 规则x’为规则x的 Lite 版，仅针对国内域名拦截，体积较小（如添加完整规则报错数量限制，请尝试 Lite 规则）\n")
            f.write("2. 已对 jsdelivr(加速链接1) 缓存进行主动刷新，但仍存在一定刷新延时\n")
            f.write("3. AdGuard 等浏览器插件使用规则1 + 规则2（规则2为规则1的补充，仅适用浏览器插件）\n")
            f.write("\n")
            tmp = "| 规则 | 原始链接 |"
            for i in range(1, len(self.proxyList)):
                tmp += " 加速链接%d |" % (i)
            tmp += " 适配说明 |\n"
            f.write(tmp)
            tmp = "|" + ":-|" * (1 + len(self.proxyList) + 1) + "\n"
            f.write(tmp)
            f.write("| 规则1 |" + self.__subscribeLink("adblockdns.txt") + " AdGuard、AdGuard Home 等 |\n")
            f.write("| 规则1' |" + self.__subscribeLink("adblockdnslite.txt") + " AdGuard、AdGuard Home 等 |\n")
            f.write("| 规则2 |" + self.__subscribeLink("adblockfilters.txt") + " AdGuard 等 |\n")
            f.write("| 规则2' |" + self.__subscribeLink("adblockfilterslite.txt") + " AdGuard 等 |\n")
            f.write("| 规则3 |" + self.__subscribeLink("adblockdomain.txt") + " InviZible Pro、personalDNSfilter |\n")
            f.write("| 规则3' |" + self.__subscribeLink("adblockdomainlite.txt") + " InviZible Pro、personalDNSfilter |\n")
            f.write("| 规则4 |" + self.__subscribeLink("adblockdnsmasq.txt") + " DNSMasq |\n")
            f.write("| 规则4' |" + self.__subscribeLink("adblockdnsmasqlite.txt") + " DNSMasq |\n")
            f.write("| 规则5 |" + self.__subscribeLink("adblocksmartdns.conf") + " SmartDNS |\n")
            f.write("| 规则5' |" + self.__subscribeLink("adblocksmartdnslite.conf") + " SmartDNS |\n")
            f.write("| 规则6 |" + self.__subscribeLink("adblockclash.list") + " Shadowrocket |\n")
            f.write("| 规则6' |" + self.__subscribeLink("adblockclashlite.list") + " Shadowrocket |\n")
            f.write("| 规则7 |" + self.__subscribeLink("adblockshadowrocket.sgmodule") + " Shadowrocket Module |\n")
            f.write("| 规则7' |" + self.__subscribeLink("adblockshadowrocketlite.sgmodule") + " Shadowrocket Module |\n")
            f.write("| 规则8 |" + self.__subscribeLink("adblockqx.conf") + " QuantumultX |\n")
            f.write("| 规则8' |" + self.__subscribeLink("adblockqxlite.conf") + " QuantumultX |\n")
            f.write("| 规则9 |" + self.__subscribeLink("adblockmihomo.yaml") + " Clash Meta(Mihomo) yaml |\n")
            f.write("| 规则9' |" + self.__subscribeLink("adblockmihomolite.yaml") + " Clash Meta(Mihomo) yaml |\n")
            f.write("| 规则10 |" + self.__subscribeLink("adblockmihomo.mrs") + " Clash Meta(Mihomo) mrs |\n")
            f.write("| 规则10' |" + self.__subscribeLink("adblockmihomolite.mrs") + " Clash Meta(Mihomo) mrs |\n")
            f.write("| 规则11 |" + self.__subscribeLink("adblockhosts.txt") + " Hosts |\n")
            f.write("| 规则11' |" + self.__subscribeLink("adblockhostslite.txt") + " Hosts |\n")
            f.write("| 规则12 |" + self.__subscribeLink("adblocksingbox.json") + " sing-box 1.12+ json |\n")
            f.write("| 规则12' |" + self.__subscribeLink("adblocksingboxlite.json") + " sing-box 1.12+ json |\n")
            f.write("| 规则13 |" + self.__subscribeLink("adblocksingbox.srs") + " sing-box 1.12+ srs |\n")
            f.write("| 规则13' |" + self.__subscribeLink("adblocksingboxlite.srs") + " sing-box 1.12+ srs |\n")
            f.write("| 规则14 |" + self.__subscribeLink("adblockloon.list") + " Loon |\n")
            f.write("| 规则14' |" + self.__subscribeLink("adblockloonlite.list") + " Loon |\n")
            f.write("| 规则15 |" + self.__subscribeLink("adblocksurge.list") + " Surge |\n")
            f.write("| 规则15' |" + self.__subscribeLink("adblocksurgelite.list") + " Surge |\n")
            f.write("| 规则16 |" + self.__subscribeLink("adblockmosdns.txt") + " MosDNS |\n")
            f.write("| 规则16' |" + self.__subscribeLink("adblockmosdnslite.txt") + " MosDNS |\n")
            f.write("| 规则17 |" + self.__subscribeLink("adblockv2ray.dat") + " V2ray、Xray(category-ads-all) |\n")
            f.write("| 规则17' |" + self.__subscribeLink("adblockv2raylite.dat") + " V2ray、Xray(category-ads-all) |\n")
            f.write("\n")

            f.write("## 上游规则源\n")
            f.write("1. 感谢各位广告过滤规则维护大佬们的辛苦付出。\n")
            f.write("2. 不再引用[anti-AD](https://anti-ad.net/adguard.txt)、[yhosts](https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts.txt)，具体原因见[Mosney/anti-anti-AD](https://github.com/Mosney/anti-anti-AD)。\n")
            f.write("3. 移除[Notracking blocklist](https://raw.githubusercontent.com/notracking/hosts-blocklists/master/adblock/adblock.txt)，原项目[已停止维护](https://github.com/notracking/hosts-blocklists/issues/900)。\n")
            f.write("4. 移除[ADgk](https://raw.githubusercontent.com/banbendalao/ADgk/master/ADgk.txt)、[SmartTV Blocklist](https://raw.githubusercontent.com/Perflyst/PiHoleBlocklist/master/SmartTV-AGH.txt)、[1024 hosts](https://raw.githubusercontent.com/Goooler/1024_hosts/master/hosts)、[ad-wars hosts](https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts)规则长时间未更新。\n")
            f.write("5. 不再引用[NEO DEV HOST](https://github.com/neodevpro/neodevhost/blob/master/lite_adblocker)，原因见[Issues 85](https://github.com/Pattern-max/adblockfilters/issues/85)。\n")
            f.write("6. 不再引用[xinggsf rule](https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/rule.txt)、[1Hosts (Lite)](https://raw.githubusercontent.com/badmojr/1Hosts/master/Lite/adblock.txt)、[Hblock](https://hblock.molinero.dev/hosts_adblock.txt)，误杀较多。\n")
            f.write("\n")

            # 生成简洁的上游规则源表格（只包含规则、类型、原始链接、更新日期，无加速链接）
            tmp = "| 规则 | 类型 | 原始链接 | 更新日期 |\n"
            f.write(tmp)
            tmp = "|" + ":-|" * 4 + "\n"
            f.write(tmp)
            for rule in self.ruleList:
                f.write("| %s | %s | [原始链接](%s) | %s |\n" % (rule.name, rule.type, rule.url, rule.latest))
            f.write("\n")