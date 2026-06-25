# selenium


## 引入selenium插件

- 首先到码云下载插件[点击下载](https://gitee.com/jmxd/spider-flow-selenium)到本地并导入到工作空间或安装到maven库
- 在spider-flow/spider-flow-web/pom.xml中引入插件


```
<!-- 引入selenium插件 -->
<dependency>
    <groupId>org.spiderflow</groupId>
    <artifactId>spider-flow-selenium</artifactId>
</dependency>
```

- 在spider-flow/spider-flow-web/application.properties中配置驱动路径
- chrome驱动下载地址：http://npm.taobao.org/mirrors/chromedriver/注意版本问题
- firefox驱动下载地址：[https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases)


## 节点说明

- 页面加载超时时间,单位为毫秒
- 元素获取超时时间,单位为毫秒
- URL:起始地址
- 节点执行完毕后，会产生`resp`类型为`SeleniumResponse`的变量


## SeleniumResponse 属性


| 字段名称 | 字段类型 | 字段描述 |
| --- | --- | --- |
| html | String | 页面HTML |
| json | JSONObject/JSONArray | 内容转json结果 |
| cookies | Map<String,String> | cookies |
| url | String | 当前页面的URL |
| title | String | 当前页面的标题 |


## SeleniumResponse 方法


### switchTo


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| index/iframeName/WebElement | 要切换的iframe | 否 |


```
${resp.switchTo(index)}
```

返回值类型：SeleniumResponse


### switchToDefault

切换至默认,即从iframe里切换回来


```
${resp.switchToDefault()}
```


### selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElement

- 获取页面上的第一个div


```
${resp.selector('div')}
```


### selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElements

- 获取页面上的所有div


```
${resp.selectors('div')}
```


### xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElement

- 获取页面上的第一个div


```
${resp.xpath('//div')}
```


### xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElements

- 获取页面上的所有div


```
${resp.xpaths('//div')}
```


### executeScript


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| script | js脚本 | 否 |
| List<Object> | 参数 | 否 |

返回值类型：Object

- 执行js


```
${resp.executeScript('return "hello spider-flow-" + arguments[0];',['selenium'])}
```


### quit

- 退出浏览器


```
${resp.quit()}
```


### toUrl


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| url | 要跳转的url | 否 |

- 跳转到百度


```
${resp.toUrl('https://www.baidu.com')}
```


### loadCookies

- 将cookie加载至cookieContext中，以便后续自动管理cookie


```
${resp.loadCookies()}
```


## WebElement 方法


### html

返回值类型：String

- 获取节点的html


```
${elementVar.html()}
```


### text

返回值类型：String

- 获取节点的text


```
${elementVar.text()}
```


### attr

返回值类型：String

- 获取节点的href属性


```
${elementVar.attr('href')}
```


### selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElement

- 获取该节点下的第一个div


```
${elementVar.selector('div')}
```


### selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElements

- 获取获取该节点下的所有div


```
${elementVar.selectors('div')}
```


### xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElement

- 获取获取该节点下的第一个div


```
${elementVar.xpath('//div')}
```


### xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElements

- 获取获取该节点下的所有div


```
${elementVar.xpaths('//div')}
```


### screenshot

返回值类型：byte[]

- 对该节点进行截图


```
${elementVar.screenshot()}
```


### click

返回值类型：WebElement

- 对该节点进行点击


```
${elementVar.click()}
```


### sendKeys

返回值类型：WebElement

- 对该节点进行模拟按键


```
${elementVar.sendKeys('hello spider-flow')}
```


### clickAndHold


### release


### move


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| offset_x | offset x | 是 |
| offset_y | offset y | 是 |

在该节点上模拟鼠标移动，当offset_x和offset_y为空时，则模拟鼠标移动到该节点上


### doubleClick


### pause


### perform

以上6个方法是配套使用，调用perform时才是真正执行动作

- 模拟鼠标移动到该节点上，等待500ms在点击，等待500ms在移动，最后释放(模拟拖拽滑块条)


```
 ${elementVar.move().pause(500).clickAndHold().pause(500).move(200,0).release().perform()}
```


## WebElements 方法


### html

返回值类型：List<String>

- 获取节点的html


```
${elementsVar.html()}
```


### text

返回值类型：List<String>

- 获取节点的text


```
${elementsVar.text()}
```


### attr

返回值类型：List<String>

- 获取节点的href属性


```
${elementsVar.attr('href')}
```


### selector


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElement

- 获取该节点下的第一个div


```
${elementsVar.selector('div')}
```


### selectors


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| cssSelector | 要获取的cssSelector | 否 |

返回值类型：WebElements

- 获取获取该节点下的所有div


```
${elementsVar.selectors('div')}
```


### xpath


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElement

- 获取获取该节点下的第一个div


```
${elementsVar.xpath('//div')}
```


### xpaths


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| xpath | 要获取的xpath | 否 |

返回值类型：WebElements

- 获取获取该节点下的所有div


```
${elementsVar.xpaths('//div')}
```
