# org.spiderflow.io.SpiderResponse


## element

返回值类型：Element

- 将对象转为Element


```
${resp.element()}
```


## xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：Element/String

- 根据xpath获取内容或Element对象


```
${resp.xpath('//a/@href')}
```


## xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：List<Element/String>

- 根据xpath获取内容或Element对象


```
${resp.xpaths('//a/@href')}
```


## regx


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：String/List<String>

- 根据正则表达式提取字符串


```
${resp.regx('<title>(.*?)</title>')}
```


## regxs


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：List<String>/List<List<String>>

- 根据正则表达式提取字符串


```
${resp.regx('<h2>(.*?)</h2>')}
```


## selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：Element

- 根据css选择器查找dom


```
${resp.selector('div a.selected')}
```


## selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：List<Element>

- 根据css选择器查找dom


```
${resp.selectors('div a.selected')}
```


## jsonpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | jsonpath | 否 |

返回值类型：Object

- 根据JSONPath提取数据


```
${resp.jsonpath('$.code')}
```


## links


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| regx | 正则表达式(有此参数时代表提取满足条件的链接) | 是 |

返回值类型：List<String>

- 提取页面上的所有a标签的链接


```
${resp.links()}
```


## images

返回值类型：List<String>

- 提取页面上的所有img的链接


```
${resp.images()}
```
