# org.jsoup.nodes.Element


## xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：Element/String

- 根据xpath获取内容或Element对象


```
${elementVar.xpath('//a/@href')}
```


## xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：List<Element/String>

- 根据xpath获取内容或Element对象


```
${elementVar.xpaths('//a/@href')}
```


## regx


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：String/List<String>

- 根据正则表达式提取字符串


```
${elementVar.regx('<title>(.*?)</title>')}
```


## regxs


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：List<String>/List<List<String>>

- 根据正则表达式提取字符串


```
${elementVar.regxs('<h2>(.*?)</h2>')}
```


## selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：Element

- 根据css选择器查找dom


```
${elementVar.selector('div a.selected')}
```


## selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：Elements

- 根据css选择器查找dom


```
${elementVar.selectors('div a.selected')}
```


## attr


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| attrName | 属性名 | 否 |

返回值类型：String

- 获取节点的属性值


```
${elementVar.attr('src')}
```


## text

返回值类型：String

- 获取节点的Text


```
${elementVar.text()}
```


## html

返回值类型：String

- 获取节点的html


```
${elementVar.html()}
```


## parent

返回值类型：Element

- 获取节点的父节点


```
${elementVar.parent()}
```


## children

返回值类型：Elements

- 获取节点的子节点


```
${elementVar.elements()}
```
