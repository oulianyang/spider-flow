# file


## write


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | 写出的路径 | 否 |
| content/bytes/stream | 内容,字符串或字节数组或二进制输入流 | 否 |
| append | 布尔类型,是否追加输出,默认为false | 是 |

无返回值

- 写出文件,内容为`hello world!`


```
${file.write('/data/test.txt','hello world!')}
```


## download


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | 写出的路径 | 否 |
| url/urls | 要下载的url或url集合 | 否 |

无返回值

- 写出文件,批量下载文件


```
${file.download('/data/',urls)}
```


## bytes


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | 要读取的文件路径 | 否 |

返回值类型：byte[]

- 读取`/data/test.txt`文件


```
${string.bytes('/data/test.txt')}
```


## string


| 参数名 | 描述 | 可否为空 |
| --- | --- | --- |
| path | 要读取的文件路径 | 否 |
| charset | 编码格式,默认为UTF-8 | 是 |

返回值类型：String

- 读取`/data/test.txt`文件


```
${string.string('/data/test.txt')}
```
