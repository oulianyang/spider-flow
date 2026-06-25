# java.lang.String


## element

返回值类型：Element

- 将字符串转为Element对象


```
${strVar.element()}
```


## xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：Element/String

- 根据xpath获取内容或Element对象


```
${strVar.xpath('//a/@href')}
```


## xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | xpath表达式 | 否 |

返回值类型：List<Element/String>

- 根据xpath获取内容或Element对象


```
${strVar.xpaths('//a/@href')}
```


## regx


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：String/List<String>

- 根据正则表达式提取字符串


```
${strVar.regx('<title>(.*?)</title>')}
```


## regxs


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 正则表达式 | 否 |
| groups | 捕获组序号int或List<Integer>(多个) | 是 |

返回值类型：List<String>/List<List<String>

- 根据正则表达式提取字符串


```
${strVar.regxs('<h2>(.*?)</h2>')}
```


## selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：Element

- 根据css选择器查找dom


```
${strVar.selector('div a.selected')}
```


## selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssQuery | css选择器 | 否 |

返回值类型：Elements

- 根据css选择器查找dom


```
${strVar.selectors('div a.selected')}
```


## json

返回值类型：Object

- 将字符串转为JSON对象


```
${strVar.json()}
```


## jsonpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | jsonpath | 否 |

返回值类型：Object

- 根据JSONPath提取数据


```
${strVar.jsonpath('$.code')}
```


### unescape

- 字符串反转义


```
${strVar.unescape()}
```


## toDate


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| pattern | 日期格式 | 否 |

返回值类型：Date

- 将字符串根据pattern转为Date类型


```
${strVar.toDate('yyyy-MM-dd HH:mm:ss')}
```


## toInt


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| defaultValue | 转换失败时的默认值 | 是 |

返回值类型：int

- 将字符串转为int类型


```
${strVar.toInt()}
```


## toDouble


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| defaultValue | 转换失败时的默认值 | 是 |

返回值类型：double

- 将字符串转为double类型


```
${strVar.toDouble()}
```


## toLong


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| defaultValue | 转换失败时的默认值 | 是 |

返回值类型：long

- 将字符串转为long类型


```
${strVar.tolong()}
```
